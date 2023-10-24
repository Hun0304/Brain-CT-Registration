
import os
import cv2
import numpy as np
import SimpleITK as sitk

from typing import Tuple
from tqdm import tqdm

from globel_veriable import CT_MAX, CT_MIN

ADJUST_WINDOW = True


# def is_supported_pixel_type(image_array):
#     """
#     Check whether the pixel type of the image is supported by SimpleITK.
#     :param image_array:
#     :return:
#     """
#     supported_pixel_types = [
#         sitk.sitkUInt8,
#         sitk.sitkUInt16,
#         sitk.sitkUInt32,
#         sitk.sitkUInt64,
#         sitk.sitkInt8,
#         sitk.sitkInt16,
#         sitk.sitkInt32,
#         sitk.sitkInt64,
#         sitk.sitkFloat32,
#         sitk.sitkFloat64,
#         sitk.sitkComplexFloat32,
#         sitk.sitkComplexFloat64
#     ]
#
#     return image_array.dtype in supported_pixel_types


# def find_center_of_mass(image: sitk.Image) -> sitk.Image:
#     """
#     將圖像中心的像素填充為黑色。
#     :param image:
#     :return:
#     """
#     image_array = sitk.GetArrayFromImage(image)
#     non_zero_indices = np.nonzero(image_array)
#     center = np.mean(non_zero_indices, axis=1)
#     # 將影像擴充至原始大小的3D空間
#     expanded_image = np.zeros_like(image_array)  # 創建一個空的3D影像
#
#     # 計算擴充後的中心位置
#     center_z, center_x, center_y = map(int, center)
#
#     # 計算擴充後的範圍
#     z_range = (expanded_image[0] - center_z).astype(np.int8)
#     x_range = (expanded_image[1] - center_x).astype(np.int8)
#     y_range = (expanded_image[2] - center_y).astype(np.int8)
#
#     # print(center_x, center_x + x_range)
#     # print(center_y, center_y + y_range)
#     print(f"{max(center_z + z_range.all(), 0) + z_range.all()=}")
#     print(f"{non_zero_indices[1]=}")
#     print(f"{image_array[non_zero_indices[1]]=}")
#     print(f"{image_array[1].shape=}")
#     print(f"{image_array[2].shape=}")
#
#     # 複製有像素範圍到擴充影像的對應位置
#     # expanded_image[center_x: center_x + x_range,
#     #                center_y: center_y + y_range,
#     #                max(center_z + z_range.all(), 0):
#     #                max(center_z + z_range.all(), 0) + z_range.all()] = image_array[non_zero_indices[1],
#     #                                                                                non_zero_indices[2],
#     #                                                                                non_zero_indices[0]]
#
#     # 至此，expanded_image就是擴充後的3D影像
#
#     # filled_image = sitk.Cast(expanded_image, sitk.sitkUInt16)
#
#     # return filled_image


def window2ct_value(ww: int, wl: int) -> Tuple[int, int]:
    """
    Convert the window width and window level to the CT value.
    :param ww: Window width.
    :param wl: Window level.
    :return: CT value.
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


def set_meta_data(save_image: sitk.Image, base_image: sitk.Image) -> sitk.Image:
    """
    Set the metadata of the image.
    :param save_image: The image to be saved.
    :param base_image: The image to be referenced.
    """
    # save_image.SetMetaData("0008|0060", save_image.GetMetaData("0008|0060"))  # Modality: CT
    # save_image.SetMetaData(metadata_inter, save_image.GetMetaData(metadata_inter))  # Rescale Intercept
    # save_image.SetMetaData(metadata_slope, save_image.GetMetaData(metadata_slope))  # Rescale Slope
    # save_image.SetMetaData(metadata_slice_thickness, save_image.GetMetaData(metadata_slice_thickness))  # Slice Thickness

    save_image.SetOrigin(base_image.GetOrigin())
    save_image.SetDirection(base_image.GetDirection())

    return save_image


def find_max_area(ct_image: np.ndarray) -> np.ndarray:
    """
    Find the max area of the contour.
    :param ct_image: The CT image.
    :return: The max area of the contour.
    """
    max_mask = []
    for i in range(ct_image.shape[0]):
        contours, _ = cv2.findContours(ct_image[i], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours) == 0:
            continue
        max_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros(ct_image[i].shape, np.uint8)
        cv2.drawContours(mask, [max_contour], 0, 255, thickness=cv2.FILLED)
        max_mask.append(mask)
    return np.array(max_mask)


def denoise(brain: np.ndarray, bone: np.ndarray) -> np.ndarray:
    """
    Denoise the image.
    :param brain: brain image.
    :param bone: bone image.
    :return: Denoised image.
    """
    denoised_image = np.zeros(bone.shape, dtype=np.uint8)
    with tqdm(total=denoised_image.shape[0], position=0) as pbar:
        pbar.set_description(desc="Denoising...")
        for i in range(denoised_image.shape[0]):
            bone_2d = bone[i, :, :]
            brain_2d = brain[i, :, :]
            for y in range(bone_2d.shape[0]):
                for x in range(bone_2d.shape[1]):
                    if bone_2d[y, x] == 255:  # 白色區域
                        denoised_image[i, y, x] = brain_2d[y, x]
            pbar.update()

    return denoised_image


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
    dicom_names = reader.GetGDCMSeriesFileNames(dcm_file_dir, series_id)
    reader.SetFileNames(dicom_names)

    image = reader.Execute()
    # window settings
    brain_dicom = sitk.IntensityWindowing(image, CT_MIN, CT_MAX, 0, 255)
    bone_setting = sitk.IntensityWindowing(image, -480, 2500, 0, 255)
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


def resample_dicom(dicom_image: sitk.Image, target_spacing=(1.0, 1.0, 1.0), mask=False) -> np.ndarray:
    """
    Resample the dicom image to space 1:1:1.
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
