
import os
import SimpleITK as sitk

from tqdm import tqdm
from glob2 import glob
from natsort import natsorted

from medical.utils import dicom2Dto3D
from mask_Resample import mask2Dto3D


def DICOM_Resample_ICH127(datasets_dicom_dir: str) -> None:
    """
    ICH_127 Datasets resample the dicom images and masks.
    :param datasets_dicom_dir: The directory of the dicom images.
    :return: None
    """
    case_list = natsorted(os.listdir(datasets_dicom_dir))
    with tqdm(total=len(case_list)) as pbar:
        for case in case_list:
            pbar.set_description(f"{case} Resample the dicom images...")
            case_bl = os.path.join(datasets_dicom_dir, case, "dcm", "BL")
            case_fu = os.path.join(datasets_dicom_dir, case, "dcm", "FU")
            dicom2Dto3D(case_bl)
            dicom2Dto3D(case_fu)
            pbar.update()

    return None


def Mask_Resample_ICH127(dataset_dir: str) -> None:
    """
    ICH_127 Datasets resample the mask images.
    :param dataset_dir: The directory of the mask images.
    :return: None
    """
    case_list = natsorted(os.listdir(dataset_dir))
    with tqdm(total=len(case_list)) as pbar:
        for case in case_list:
            pbar.set_description(f"{case} Resample the mask images...")
            mask_bl = os.path.join(dataset_dir, case, "mask", "BL")
            mask_fu = os.path.join(dataset_dir, case, "mask", "FU")
            dicom_bl = os.path.join(dataset_dir, case, "dcm", "BL")
            dicom_fu = os.path.join(dataset_dir, case, "dcm", "FU")
            mask2Dto3D(mask_bl, dicom_bl)
            mask2Dto3D(mask_fu, dicom_fu)
            pbar.update()

    return None


def Mask_Resample_Back_ICH127(dir: str):
    """
    ICH_127 Dataset resample the mask back to the original size.
    :param dir: The directory of the mask.
    :return: None
    """
    case_list = natsorted(os.listdir(dir))
    with tqdm(total=len(case_list)) as pbar:
        for case in case_list:
            pbar.set_description(f"ICH127 {case} 3D mask resample back...")
            regis_mask = glob(os.path.join(dir, case, "registration result", "registered-mask-*.dcm"))[-1]
            bl_mask = os.path.join(dir, case, "mask", "result", f"{case}-1-mask.dcm")
            ori_mask = sitk.ReadImage(bl_mask, sitk.sitkFloat32)
            reg_mask = sitk.ReadImage(regis_mask, sitk.sitkFloat32)
            reg_mask = sitk.Resample(reg_mask, ori_mask, sitk.Transform(), sitk.sitkNearestNeighbor, 0.0, reg_mask.GetPixelID())
            reg_mask.CopyInformation(ori_mask)
            reg_mask = sitk.Cast(reg_mask, sitk.sitkUInt16)
            sitk.WriteImage(reg_mask, os.path.join(dir, case, "mask", "result", f"{case}-registered-mask.dcm"))
            pbar.update()

    return None
