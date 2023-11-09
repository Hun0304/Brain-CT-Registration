
import re
import os
import numpy as np
import SimpleITK as sitk

from tqdm import tqdm
from natsort import natsorted

from common.globel_veriable import REGISTRATION_DIR_420, BRAIN_CT_MIN, BRAIN_CT_MAX, BONE_CT_MIN, BONE_CT_MAX
from common.image_process import find_max_area, denoise
from medical.utils import set_meta_data, resample_dicom


def DICOM_Resample_ICH420(datasets_dicom_dir: str) -> None:
    """
    ICH_420 Datasets resample the dicom images.
    :param datasets_dicom_dir: The directory of the dicom images.
    :return: None
    """
    dicom_list = natsorted(os.listdir(datasets_dicom_dir))
    patten = r'Case_\d+-\d+|Spon_Case_\d+-\d+'
    flip_axes = (False, True, False)
    with tqdm(total=len(dicom_list)) as pbar:
        for dicom in dicom_list:
            case_name = re.search(patten, dicom).group(0)
            pbar.set_description(f"{case_name} Resample the dicom images...")
            if case_name in dicom:
                dicom = sitk.ReadImage(os.path.join(datasets_dicom_dir, dicom), sitk.sitkFloat32)
                dicom = sitk.Flip(dicom, flip_axes)
                brain_dicom = sitk.IntensityWindowing(dicom, BRAIN_CT_MIN, BRAIN_CT_MAX, 0, 255)
                bone_setting = sitk.IntensityWindowing(dicom, BONE_CT_MIN, BONE_CT_MAX, 0, 255)
                bone_dicom = sitk.OtsuThreshold(bone_setting, 0, 1)
                # denoise
                brain_image = sitk.GetArrayFromImage(brain_dicom)
                bone_image = find_max_area(sitk.GetArrayFromImage(bone_dicom))
                if brain_image.shape != bone_image.shape:
                    # bone image add black slice
                    black_slice = np.zeros((brain_image.shape[0] - bone_image.shape[0],
                                            bone_image.shape[1],
                                            bone_image.shape[2]))
                    bone_image = np.append(bone_image, black_slice, axis=0)
                brain_denoised_image = denoise(brain_image, bone_image)
                brain_denoised_dicom = sitk.GetImageFromArray(brain_denoised_image)
                brain_denoised_dicom.CopyInformation(dicom)
                brain_resampled_array = resample_dicom(brain_denoised_dicom)
                brain_resampled_image = sitk.GetImageFromArray(brain_resampled_array)
                brain_resampled_image = set_meta_data(brain_resampled_image, dicom)

                bone_resample_dicom = sitk.GetImageFromArray(bone_image)
                bone_resample_dicom.CopyInformation(dicom)
                bone_resample_array = resample_dicom(bone_resample_dicom, mask=True)
                bone_resample_image = sitk.GetImageFromArray(bone_resample_array)
                bone_resample_image = set_meta_data(bone_resample_image, dicom)

                brain_denoised_dicom = sitk.Cast(brain_denoised_dicom, sitk.sitkUInt16)
                brain_resampled_image = sitk.Cast(brain_resampled_image, sitk.sitkUInt16)
                bone_resample_image = sitk.Cast(bone_resample_image, sitk.sitkUInt16)
                brain_image = sitk.Cast(sitk.GetImageFromArray(brain_image), sitk.sitkUInt16)
                bone_image = sitk.Cast(sitk.GetImageFromArray(bone_image), sitk.sitkUInt16)

                dir_name = case_name.replace("_", " ")
                case_number = dir_name.split("-")[0]
                bl_fu = dir_name.split("-")[1]
                output_path = os.path.join(REGISTRATION_DIR_420, case_number, "dcm", "result")
                os.makedirs(output_path, exist_ok=True)
                sitk.WriteImage(brain_image, os.path.join(output_path, f"{case_number}-{bl_fu}-brain.nii.gz"))
                sitk.WriteImage(bone_image, os.path.join(output_path, f"{case_number}-{bl_fu}-bone.nii.gz"))
                sitk.WriteImage(brain_denoised_dicom, os.path.join(output_path, f"{case_number}-{bl_fu}-brain-denoised.nii.gz"))
                sitk.WriteImage(brain_resampled_image, os.path.join(output_path, f"{case_number}-{bl_fu}-brain-resample.nii.gz"))
                sitk.WriteImage(bone_resample_image, os.path.join(output_path, f"{case_number}-{bl_fu}-bone-resample.nii.gz"))
            pbar.update()
    return None


def Mask_Resample_ICH420(datasets_mask_dir: str) -> None:
    """
    ICH_420 Dataset resample the mask back to the original size.
    :param datasets_mask_dir: The directory of the mask.
    :return: None
    """
    mask_list = natsorted(os.listdir(datasets_mask_dir))
    patten = r'Case_\d+-\d+|Spon_Case_\d+-\d+'
    flip_axes = (False, True, False)
    with tqdm(total=len(mask_list)) as pbar:
        for mask in mask_list:
            case_name = re.search(patten, mask).group(0)
            pbar.set_description(f"{case_name} Resample the mask images...")
            if case_name in mask:
                mask = sitk.ReadImage(os.path.join(datasets_mask_dir, mask), sitk.sitkFloat32)
                mask = sitk.Flip(mask, flip_axes)
                res_mask = resample_dicom(mask, mask=True)
                res_mask = np.where(res_mask > 0, 255, 0)
                res_mask = sitk.GetImageFromArray(res_mask)
                res_mask = set_meta_data(res_mask, mask)

                case_number = case_name.split("-")[0].replace("_", " ")
                bl_fu = case_name.split("-")[1]
                output_path = os.path.join(REGISTRATION_DIR_420, case_number, "mask", "result")
                os.makedirs(output_path, exist_ok=True)
                mask = sitk.GetArrayFromImage(mask)
                mask = np.where(mask > 0, 255, 0)
                mask = sitk.GetImageFromArray(mask)
                mask = sitk.Cast(mask, sitk.sitkUInt16)
                res_mask = sitk.Cast(res_mask, sitk.sitkUInt16)
                sitk.WriteImage(mask, os.path.join(output_path, f"{case_number}-{bl_fu}-mask.nii.gz"))
                sitk.WriteImage(res_mask, os.path.join(output_path, f"{case_number}-{bl_fu}-mask-resample.nii.gz"))
            pbar.update()

    return None
