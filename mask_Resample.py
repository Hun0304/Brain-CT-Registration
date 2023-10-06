
import os
import cv2
import numpy as np
import SimpleITK as sitk

from natsort import natsorted
from typing import List
from datetime import date

from globel_veriable import CASE_DIR
from DICOM_Resample import resample_dicom


def merge_image(masks: List, mask_dir: str) -> None:
    """
    Merge the masks with the same name.
    :param masks: The list of masks.
    :param mask_dir: The directory of masks.
    :return: None
    """
    temp = masks[0]
    for mask in masks[1:]:
        name = mask[:mask.rfind("-")]
        if temp[:temp.rfind("-")] == name:
            image_1 = cv2.imread(os.path.join(mask_dir, mask))
            image_2 = cv2.imread(os.path.join(mask_dir, temp))
            merge = cv2.add(image_1, image_2)
            cv2.imwrite(os.path.join(mask_dir, name + ".tif"), merge)
            os.remove(os.path.join(mask_dir, mask))
            os.remove(os.path.join(mask_dir, temp))
        else:
            temp = mask
    return None


def mask2Dto3D(mask_dir: str, dicom_dir: str) -> None:
    """
    Merge the masks with the same name and convert them to 3D.
    :param mask_dir: The directory of masks.
    :param dicom_dir: The directory of dicom images.
    :param merge: Whether to merge the masks.
    :return: None
    """
    mask_list = natsorted(os.listdir(mask_dir))
    if "p" in mask_list[0] or "v" in mask_list[0]:
        merge_image(mask_list, mask_dir)
        mask_list = natsorted(os.listdir(mask_dir))

    for mask in mask_list:
        if "p" in mask or "v" in mask:
            os.rename(os.path.join(mask_dir, mask), os.path.join(mask_dir, mask[:mask.rfind("-")] + ".tif"))
    mask_list = natsorted(os.listdir(mask_dir))

    reader = sitk.ImageSeriesReader()
    series_ids = reader.GetGDCMSeriesIDs(dicom_dir)
    series_id = series_ids[0]
    dicom_names = reader.GetGDCMSeriesFileNames(dicom_dir, series_id)
    reader.SetFileNames(dicom_names)
    dicom_image = reader.Execute()

    # Create 3D mask
    mask_3d = np.zeros((len(dicom_names), dicom_image.GetSize()[0], dicom_image.GetSize()[1]), dtype=np.uint16)
    for i in range(len(dicom_names)):
        for mask in mask_list:
            if mask[mask.rfind("-")+1:mask.rfind(".")] == str(i):
                image = cv2.imread(os.path.join(mask_dir, mask), cv2.IMREAD_GRAYSCALE)
                mask_3d[i, :, :] = image

    print(mask_3d.shape)
    mask_dcm = sitk.GetImageFromArray(mask_3d.astype(np.uint16))

    mask_dcm.CopyInformation(dicom_image)
    print(f"{mask_dcm.GetSpacing()=}")
    print(f"{mask_dcm.GetOrigin()=}")
    print(f"{mask_dcm.GetDirection()=}")
    resample_mask = resample_dicom(mask_dcm, mask=True)
    resample_mask = sitk.GetImageFromArray(resample_mask.astype(np.uint16))
    resample_mask.SetOrigin(dicom_image.GetOrigin())
    resample_mask.SetDirection(dicom_image.GetDirection())
    print(f"{resample_mask.GetOrigin()=}")
    print(f"{resample_mask.GetDirection()=}")

    output_path = os.path.abspath(os.path.join(mask_dir, "..", "result"))
    os.makedirs(output_path, exist_ok=True)
    mask_filename = os.path.join(output_path, mask_list[0][:mask_list[0].rfind("-")] + "-mask" + ".dcm")
    resample_mask_filename = os.path.join(output_path, mask_list[0][:mask_list[0].rfind("-")] + "-mask-resample" + ".dcm")
    mask_dcm = sitk.Cast(mask_dcm, sitk.sitkUInt16)
    resample_mask = sitk.Cast(resample_mask, sitk.sitkUInt16)
    sitk.WriteImage(mask_dcm, mask_filename)
    sitk.WriteImage(resample_mask, resample_mask_filename)

    # mask_resample_back(mask_filename, resample_mask_filename)

    return None


def mask_resample_back(origin_mask, regis_mask) -> None:
    """
    Resample the mask back to the original size.
    :param origin_mask: The original mask.
    :param regis_mask: The registered mask.
    :return: None
    """
    ori_mask = sitk.ReadImage(origin_mask, sitk.sitkFloat32)
    reg_mask = sitk.ReadImage(regis_mask, sitk.sitkFloat32)
    reg_mask = sitk.Resample(reg_mask, ori_mask, sitk.Transform(), sitk.sitkNearestNeighbor, 0.0, reg_mask.GetPixelID())
    reg_mask.CopyInformation(ori_mask)
    reg_mask = sitk.Cast(reg_mask, sitk.sitkUInt16)
    os.makedirs(os.path.join(CASE_DIR, "registration"), exist_ok=True)
    sitk.WriteImage(reg_mask, os.path.join(CASE_DIR, "registration", f"registered-back-mask-{date.today()}.dcm"))
    return None
