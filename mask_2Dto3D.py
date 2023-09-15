
import os
import cv2
import numpy as np
import SimpleITK as sitk

from natsort import natsorted
from typing import List

from DICOM_2D_to_3D import resample_dicom


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
            # print(os.path.join(mask_dir, mask))
            # print(os.path.join(mask_dir, temp))
            image_1 = cv2.imread(os.path.join(mask_dir, mask))
            image_2 = cv2.imread(os.path.join(mask_dir, temp))
            merge = cv2.add(image_1, image_2)
            cv2.imwrite(os.path.join(mask_dir, name + ".tif"), merge)
            os.remove(os.path.join(mask_dir, mask))
            os.remove(os.path.join(mask_dir, temp))
        else:
            temp = mask


def mask2Dto3D(mask_dir: str, dicom_dir: str, merge=False) -> None:
    """
    Merge the masks with the same name and convert them to 3D.
    :param mask_dir: The directory of masks.
    :param dicom_dir: The directory of dicom images.
    :param merge: Whether to merge the masks.
    :return: None
    """
    mask_list = natsorted(os.listdir(mask_dir))
    if merge:
        merge_image(mask_list, mask_dir)
    mask_list = [f for f in mask_list if f.endswith(".tif")]

    for mask in mask_list:
        if "p" in mask or "v" in mask:
            os.rename(os.path.join(mask_dir, mask), os.path.join(mask_dir, mask[:mask.rfind("-")] + ".tif"))

    reader = sitk.ImageSeriesReader()
    series_ids = reader.GetGDCMSeriesIDs(dicom_dir)
    series_id = series_ids[0]
    dicom_names = reader.GetGDCMSeriesFileNames(dicom_dir, series_id)
    reader.SetFileNames(dicom_names)
    dicom_image = reader.Execute()

    mask_3d = np.zeros((len(dicom_names), dicom_image.GetSize()[0], dicom_image.GetSize()[1]), dtype=np.uint16)
    for i in range(len(dicom_names)):
        for mask in mask_list:
            if mask[mask.rfind("-")+1:mask.rfind(".")] == str(i):
                print(i)
                image = cv2.imread(os.path.join(mask_dir, mask), cv2.IMREAD_GRAYSCALE)
                mask_3d[i, :, :] = image

    print(mask_3d.shape)
    mask_dcm = sitk.GetImageFromArray(mask_3d.astype(np.uint16))

    mask_dcm.CopyInformation(dicom_image)
    # mask_dcm.SetSpacing(dicom_image.GetSpacing())
    # mask_dcm.SetOrigin(dicom_image.GetOrigin())
    # mask_dcm.SetDirection(dicom_image.GetDirection())
    print(f"{mask_dcm.GetSpacing()=}")
    print(f"{mask_dcm.GetOrigin()=}")
    print(f"{mask_dcm.GetDirection()=}")
    resample_mask = resample_dicom(mask_dcm, mask=True)
    resample_mask = sitk.GetImageFromArray(resample_mask.astype(np.uint16))
    resample_mask.SetOrigin(dicom_image.GetOrigin())
    resample_mask.SetDirection(dicom_image.GetDirection())
    print(f"{resample_mask.GetOrigin()=}")
    print(f"{resample_mask.GetDirection()=}")

    mask_name = os.path.join(mask_dir, mask_list[0][:mask_list[0].rfind("-")] + "-mask" + ".dcm")
    resample_mask_name = os.path.join(mask_dir, mask_list[0][:mask_list[0].rfind("-")] + "-mask-resample" + ".dcm")
    sitk.WriteImage(mask_dcm, mask_name)
    sitk.WriteImage(resample_mask, resample_mask_name)

    return None


if __name__ == '__main__':
    mask_path = r"C:\Users\Hun\Desktop\127 test\BL_Mask"
    dicom_path = r"C:\Users\Hun\Desktop\127 test\BL"
    mask2Dto3D(mask_path, dicom_path)
