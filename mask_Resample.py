
import os
import cv2
import numpy as np
import SimpleITK as sitk

from tqdm import tqdm
from datetime import date
from natsort import natsorted

from medical.utils import set_meta_data, resample_dicom
from common.globel_veriable import REGISTRATION_DIR_127
from common.image_process import merge_image


def mask2Dto3D(mask_dir: str, dicom_dir: str) -> None:
    """
    Merge the masks with the same name and convert them to 3D.
    :param mask_dir: The directory of masks.
    :param dicom_dir: The directory of dicom images.
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

    mask_dcm = sitk.GetImageFromArray(mask_3d.astype(np.uint16))
    mask_dcm.CopyInformation(dicom_image)
    resample_mask = resample_dicom(mask_dcm, mask=True)
    resample_mask = sitk.GetImageFromArray(resample_mask.astype(np.uint16))
    resample_mask = set_meta_data(resample_mask, dicom_image)

    output_path = os.path.abspath(os.path.join(mask_dir, "..", "result"))
    os.makedirs(output_path, exist_ok=True)
    mask_filename = os.path.join(output_path, f"{mask_list[0][:mask_list[0].rfind('-')]}-mask.dcm")
    resample_mask_filename = os.path.join(output_path, f"{mask_list[0][:mask_list[0].rfind('-')]}-mask-resample.dcm")
    mask_dcm = sitk.Cast(mask_dcm, sitk.sitkUInt16)
    resample_mask = sitk.Cast(resample_mask, sitk.sitkUInt16)
    sitk.WriteImage(mask_dcm, mask_filename)
    sitk.WriteImage(resample_mask, resample_mask_filename)

    return None


def mask_resample_back() -> None:
    """
    Resample the mask back to the original size.
    :return: None
    """
    no_mask_list = ["Case 25", "Case 70", "Case 156", "Case 299", "Case 319", "Case 327", "Case 329", "Case 337"]
    case_list = natsorted(os.listdir(REGISTRATION_DIR_127))
    with tqdm(total=len(case_list)) as pbar:
        for case in case_list:
            pbar.set_description(f"{case} 3D mask resample back...")
            if case in no_mask_list:
                pbar.update()
                continue
            origin_mask = os.path.join(REGISTRATION_DIR_127, case, "mask", "result", f"{case}-1-mask.dcm")
            regis_mask = os.path.join(REGISTRATION_DIR_127, case, "registration result", f"registered-mask-{date.today()}.dcm")
            ori_mask = sitk.ReadImage(origin_mask, sitk.sitkFloat32)
            reg_mask = sitk.ReadImage(regis_mask, sitk.sitkFloat32)
            reg_mask = sitk.Resample(reg_mask, ori_mask, sitk.Transform(), sitk.sitkNearestNeighbor, 0.0, reg_mask.GetPixelID())
            reg_mask.CopyInformation(ori_mask)
            reg_mask = sitk.Cast(reg_mask, sitk.sitkUInt16)
            sitk.WriteImage(reg_mask, os.path.join(REGISTRATION_DIR_127, case, "mask", "result", f"registered-back-mask-{date.today()}.dcm"))
            pbar.update()

    return None
