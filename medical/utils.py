import os
import numpy as np
import SimpleITK as sitk

from typing import Any, Tuple
from natsort import natsorted
from collections import namedtuple

from common.globel_veriable import BRAIN_WINDOW, BONE_WINDOW
from common.image_process import find_max_area, denoise


def get_meta_data(dicom_path: str, metadata_tag: str, show_all: bool = 0) -> Any:
    """
    Get the metadata of the image.
    :param dicom_path: dicom file path.
    :param metadata_tag: The metadata of the image.
    :param show_all: Whether to get all metadata.
    :return: None
    """
    dicom = sitk.ReadImage(dicom_path)
    case_name = dicom_path[dicom_path.rfind("\\") + 1:dicom_path.rfind("-")]

    if show_all:
        for key in dicom.GetMetaDataKeys():
            print(f"{key} = {dicom.GetMetaData(key).encode('utf-8', 'replace')}")
        return None

    return case_name, dicom.GetMetaData(metadata_tag).encode('utf-8', 'replace')


def set_meta_data(save_image: sitk.Image, base_image: sitk.Image) -> sitk.Image:
    """
    Set the metadata of the image.
    :param save_image: The image to be saved.
    :param base_image: The image to be referenced.
    """

    save_image.SetOrigin(base_image.GetOrigin())
    save_image.SetDirection(base_image.GetDirection())

    return save_image


def resample_dicom(dicom_image: sitk.Image, target_spacing=(1.0, 1.0, 1.0), mask=False) -> np.ndarray:
    """
    Resample the dicom image.
    :param dicom_image: The dicom image.
    :param mask: Whether the image is mask.
    :type target_spacing: The target spacing.
    """
    original_shape = dicom_image.GetSize()
    original_spacing = dicom_image.GetSpacing()
    target_shape = [int(round(original_shape[0] * (original_spacing[0] / target_spacing[0]))),
                    int(round(original_shape[1] * (original_spacing[1] / target_spacing[1]))),
                    int(round(original_shape[2] * (original_spacing[2] / target_spacing[2])))]

    scaling_factors = np.divide(original_spacing, target_spacing)
    interpolator = sitk.sitkNearestNeighbor if mask else sitk.sitkLinear
    resample_image = sitk.Resample(dicom_image,
                                   target_shape,
                                   sitk.Transform(),
                                   interpolator,
                                   dicom_image.GetOrigin(),
                                   target_spacing,
                                   dicom_image.GetDirection(),
                                   0.0,
                                   dicom_image.GetPixelIDValue())

    return sitk.GetArrayFromImage(resample_image)


def window2ct_value(wl: int, ww: int) -> Tuple[int, int]:
    """
    Convert the window level and window width to the CT value.
    :param wl: Window level.
    :param ww: Window width.
    :return: CT value min, CT value max.
    """
    return wl - ww // 2, wl + ww // 2


def ct_value2window(ct_min: int, ct_max: int) -> Tuple[int, int]:
    """
    Convert the CT value to the window width and window level.
    :param ct_min:
    :param ct_max:
    :return: Window width and window level.
    """
    return ct_max - ct_min, (ct_max + ct_min) // 2


def dicom2Dto3D(dcm_file_dir: str) -> None:
    """
    Convert 2D dicom images to 3D dicom image.
    :param dcm_file_dir: The directory of dicom images.
    """
    reader = sitk.ImageSeriesReader()
    series_ids = reader.GetGDCMSeriesIDs(dcm_file_dir)
    if not series_ids:
        print("ERROR: No DICOM series found in the specified folder.")
        exit(1)
    series_id = series_ids[0]
    dicom_names = natsorted(reader.GetGDCMSeriesFileNames(dcm_file_dir, series_id))
    reader.SetFileNames(dicom_names)

    image = reader.Execute()

    # window settings
    brain_dicom = sitk.IntensityWindowing(image, BRAIN_WINDOW.CT_MIN, BRAIN_WINDOW.CT_MAX, 0, 255)
    bone_setting = sitk.IntensityWindowing(image, BONE_WINDOW.CT_MIN, BONE_WINDOW.CT_MAX, 0, 255)
    bone_dicom = sitk.OtsuThreshold(bone_setting, 0, 1)
    # bone_setting = sitk.Cast(bone_setting, sitk.sitkUInt16)

    # denoise
    brain_image = sitk.GetArrayFromImage(brain_dicom)
    bone_image = find_max_area(sitk.GetArrayFromImage(bone_dicom))
    if brain_image.shape != bone_image.shape:
        # bone image add black slice
        black_slice = np.zeros((brain_image.shape[0] - bone_image.shape[0],
                                bone_image.shape[1],
                                bone_image.shape[2]), dtype=np.uint16)
        bone_image = np.append(bone_image, black_slice, axis=0)
    brain_denoised_image = denoise(brain_image, bone_image)
    brain_denoised_dicom = sitk.GetImageFromArray(brain_denoised_image.astype(np.uint16))
    brain_denoised_dicom.CopyInformation(image)

    brain_resampled_array = resample_dicom(brain_denoised_dicom)
    brain_resampled_image = sitk.GetImageFromArray(brain_resampled_array.astype(np.uint16))
    brain_resampled_image = set_meta_data(brain_resampled_image, image)

    bone_resample_dicom = sitk.GetImageFromArray(bone_image.astype(np.uint16))
    bone_resample_dicom.CopyInformation(image)
    bone_resample_array = resample_dicom(bone_resample_dicom, mask=True)
    bone_resample_image = sitk.GetImageFromArray(bone_resample_array.astype(np.uint16))
    bone_resample_image = set_meta_data(bone_resample_image, image)

    output_path = os.path.abspath(os.path.join(dcm_file_dir, "..", "result"))
    os.makedirs(output_path, exist_ok=True)
    case_number = dicom_names[0][dicom_names[0].rfind("\\") + 1:dicom_names[0].rfind("-")]  # Case 1-1 or Case 1-2
    sitk.WriteImage(sitk.GetImageFromArray(brain_image.astype(np.uint16)),
                    os.path.join(output_path, f"{case_number}-brain.dcm"))
    sitk.WriteImage(sitk.GetImageFromArray(bone_image.astype(np.uint16)),
                    os.path.join(output_path, f"{case_number}-bone.dcm"))
    sitk.WriteImage(brain_denoised_dicom, os.path.join(output_path, f"{case_number}-brain-denoised.dcm"))
    sitk.WriteImage(brain_resampled_image, os.path.join(output_path, f"{case_number}-brain-resample.dcm"))
    sitk.WriteImage(bone_resample_image, os.path.join(output_path, f"{case_number}-bone-resample.dcm"))
    # sitk.WriteImage(bone_setting, os.path.join(output_path, f"{case_number}-bone-setting.dcm"))

    return None


class Calculator:
    """
    The class of calculator.
    """

    def __init__(self):
        pass

    @staticmethod
    def calc_correlation(img_bl: str, img_fu: str) -> Any:
        """
        Calculate the correlation between two images.
        :param img_bl: The baseline image.
        :param img_fu: The follow-up image.
        :return: The correlation between two images.
        """
        dicom_bl = sitk.ReadImage(img_bl, sitk.sitkFloat32)
        dicom_fu = sitk.ReadImage(img_fu, sitk.sitkFloat32)
        bl_array = sitk.GetArrayFromImage(dicom_bl)
        fu_array = sitk.GetArrayFromImage(dicom_fu)

        correlation_value = np.corrcoef(bl_array.flatten(), fu_array.flatten())[0, 1]

        print(f"correlation value: {correlation_value}")
        return correlation_value

    @staticmethod
    def calc_he(mask_bl: str, mask_fu: str) -> namedtuple:
        """
        Calculate the Hematoma Expansion.
        :param mask_bl: The baseline mask.
        :param mask_fu: The follow-up mask.
        :return: baseline volume, follow volume, volume change,
                 volume change rate, Hematoma Expansion.
        """

        def calc_volume(mask: str) -> float:
            """
            Calculate the volume of the mask.
            :param mask: The mask.
            :return: The volume of the mask.
            """
            mask_image = sitk.ReadImage(mask, sitk.sitkFloat32)
            mask_array = sitk.GetArrayFromImage(mask_image)
            mask_array = np.where(mask_array > 0, 1, 0)

            voxel_volume = np.prod(mask_image.GetSpacing())
            volume = np.sum(mask_array) * voxel_volume

            return volume

        VolumeData = namedtuple("VolumeData",
                                ["volume_bl", "volume_fu", "volume_change", "volume_change_rate", "he"])

        volume_bl = calc_volume(mask_bl) / 1000
        volume_fu = calc_volume(mask_fu) / 1000

        volume_change = volume_fu - volume_bl
        volume_change_rate = volume_change / volume_bl
        he = 1 if volume_change_rate >= 0.33 or volume_change >= 6 else 0

        return VolumeData(volume_bl, volume_fu, volume_change, volume_change_rate, he)
