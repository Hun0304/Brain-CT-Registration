
import os

from typing import Tuple


def create_dir(dir) -> Tuple[str, str, str, str]:
    """
    Create directory.
    :param dir: The directory of the images.
    :return: The directory of the images.
    """
    dicom_bl_dir = os.path.join(dir, "dcm", "BL")
    dicom_fu_dir = os.path.join(dir, "dcm", "FU")
    mask_bl_dir = os.path.join(dir, "mask", "BL")
    mask_fu_dir = os.path.join(dir, "mask", "FU")

    os.makedirs(dicom_bl_dir, exist_ok=True)
    os.makedirs(dicom_fu_dir, exist_ok=True)
    os.makedirs(mask_bl_dir, exist_ok=True)
    os.makedirs(mask_fu_dir, exist_ok=True)

    return dicom_bl_dir, dicom_fu_dir, mask_bl_dir, mask_fu_dir
