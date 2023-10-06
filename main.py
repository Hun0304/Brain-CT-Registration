
import os
from typing import Tuple

from DICOM_Resample import dicom2Dto3D
from mask_Resample import mask2Dto3D
from globel_veriable import CASE_DIR


def create_dir() -> Tuple[str, str, str, str]:
    """
    Create directory.
    :return: None
    """
    dicom_bl_dir = os.path.join(CASE_DIR, "dcm", "BL")
    dicom_fu_dir = os.path.join(CASE_DIR, "dcm", "FU")
    mask_bl_dir = os.path.join(CASE_DIR, "mask", "BL")
    mask_fu_dir = os.path.join(CASE_DIR, "mask", "FU")

    os.makedirs(dicom_bl_dir, exist_ok=True)
    os.makedirs(dicom_fu_dir, exist_ok=True)
    os.makedirs(mask_bl_dir, exist_ok=True)
    os.makedirs(mask_fu_dir, exist_ok=True)

    return dicom_bl_dir, dicom_fu_dir, mask_bl_dir, mask_fu_dir


def main():
    """
    Main function.
    """
    dicom_bl_dir, dicom_fu_dir, mask_bl_dir, mask_fu_dir = create_dir()
    # dicom2Dto3D(dicom_bl_dir)
    # dicom2Dto3D(dicom_fu_dir)
    # mask2Dto3D(mask_bl_dir, dicom_bl_dir, merge=True)
    mask2Dto3D(mask_fu_dir, dicom_bl_dir)


if __name__ == '__main__':
    main()
