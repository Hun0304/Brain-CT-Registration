
import os
import cv2
import numpy as np
# noinspection PyPep8Naming
import SimpleITK as sitk
import matplotlib.pyplot as plt

from typing import Tuple
from tqdm import tqdm


# window settings
CT_min, CT_max = 0, 80     # brain WW: 80, WL: 40
# CT_min, CT_max = -20, 180  # subdural WW: 200, WL: 80
# CT_min, CT_max = -800, 2000  # temporal bone WW: 2800, WL: 600

window_width, window_level = CT_max - CT_min, (CT_max + CT_min) // 2

ADJUST_WINDOW = True


def window2ct_value(ww, wl) -> Tuple[int, int]:
    """
    Convert the window width and window level to the CT value.
    :param ww: Window width.
    :param wl: Window level.
    :return: CT value.
    """
    return wl - ww // 2, wl + ww // 2


def ct_value2window(ct_min, ct_max) -> Tuple[int, int]:
    """
    Convert the CT value to the window width and window level.
    :param ct_min:
    :param ct_max:
    :return: Window width and window level.
    """
    return ct_max - ct_min, (ct_max + ct_min) // 2


def set_meta_data(base_image: sitk.Image, save_image: sitk.Image, is_resample=False) -> sitk.Image:
    """
    Set the metadata of the image.
    :param base_image: The image to be referenced.
    :param save_image: The image to be saved.
    :param is_resample: Whether to resample the image.
    """
    # save_image.SetMetaData("0008|0060", save_image.GetMetaData("0008|0060"))  # Modality: CT
    # save_image.SetMetaData(metadata_inter, save_image.GetMetaData(metadata_inter))  # Rescale Intercept
    # save_image.SetMetaData(metadata_slope, save_image.GetMetaData(metadata_slope))  # Rescale Slope
    # save_image.SetMetaData(metadata_slice_thickness, save_image.GetMetaData(metadata_slice_thickness))  # Slice Thickness

    save_image.SetOrigin(base_image.GetOrigin())
    save_image.SetDirection(base_image.GetDirection())
    if not is_resample:
        save_image.SetSpacing(base_image.GetSpacing())

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
    print(bone.shape)

    for i in tqdm(range(denoised_image.shape[0]), desc="Denoising..."):
        bone_2d = bone[i, :, :]
        brain_2d = brain[i, :, :]
        for y in range(bone_2d.shape[0]):
            for x in range(bone_2d.shape[1]):
                if bone_2d[y, x] == 255:  # 白色區域
                    denoised_image[i, y, x] = brain_2d[y, x]
    return denoised_image


def dicom2Dto3D(dcm_file_dir) -> None:
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
    print(f'{dicom_names=}')
    reader.SetFileNames(dicom_names)

    image = reader.Execute()

    # window settings
    brain_dicom = sitk.IntensityWindowing(image, 0, 80, 0, 255)
    bone_dicom = sitk.OtsuThreshold(image, 0, 1, 200)

    print(f"{brain_dicom.GetOrigin()=}")
    print(f"{brain_dicom.GetSpacing()=}")
    print(f"{brain_dicom.GetDirection()=}")

    # denoise
    brain_image = sitk.GetArrayFromImage(brain_dicom)
    bone_image = find_max_area(sitk.GetArrayFromImage(bone_dicom))
    denoised_image = denoise(brain_image, bone_image).astype(np.uint16)

    denoised_dicom = sitk.GetImageFromArray(denoised_image)
    denoised_dicom.CopyInformation(brain_dicom)
    # denoised_dicom = set_meta_data(brain_dicom, denoised_dicom)
    resampled_array = resample_dicom(denoised_dicom) if ADJUST_WINDOW else resample_dicom(image)
    print(f'{resampled_array.shape=}')
    resampled_image = sitk.GetImageFromArray(resampled_array.astype(np.uint16))
    resampled_image.CopyInformation(brain_dicom)
    # resampled_image = set_meta_data(brain_dicom, resampled_image, is_resample=True)

    bone_resample_dicom = sitk.GetImageFromArray(bone_image.astype(np.uint16))
    bone_resample_dicom.CopyInformation(brain_dicom)
    # bone_resample_dicom = set_meta_data(brain_dicom, bone_resample_dicom)
    bone_resample_array = resample_dicom(bone_resample_dicom, mask=True)
    bone_resample_image = sitk.GetImageFromArray(bone_resample_array.astype(np.uint16))
    # bone_resample_image = set_meta_data(brain_dicom, bone_resample_image, is_resample=True)
    bone_resample_image.CopyInformation(brain_dicom)

    output_path = r'C:\Users\Hun\Desktop\127 test\new_0825'
    os.makedirs(output_path, exist_ok=True)
    sitk.WriteImage(sitk.GetImageFromArray(brain_image.astype(np.uint16)), os.path.join(output_path, "Case 1-1_brain.dcm"))
    sitk.WriteImage(sitk.GetImageFromArray(bone_image), os.path.join(output_path, "Case 1-1_bone.dcm"))
    sitk.WriteImage(denoised_dicom, os.path.join(output_path, "Case 1-1_denoised_brain.dcm"))
    sitk.WriteImage(resampled_image, os.path.join(output_path, "Case 1-1_brain_resample.dcm"))
    sitk.WriteImage(bone_resample_image, os.path.join(output_path, "Case 1-1_bone_resample.dcm"))

    return None


# def read_dicom_file(dcm_file_dir, filename):
#     """
#     Read the dicom file.
#     :param dcm_file_dir:
#     :param filename:
#     """
#     dcm_file = os.path.join(dcm_file_dir, filename)
#     image_reader = sitk.ImageFileReader()
#     image_reader.SetImageIO("GDCMImageIO")
#     image_reader.SetFileName(dcm_file)
#     image_reader.ReadImageInformation()
#
#     image = sitk.ReadImage(dcm_file, sitk.sitkFloat32)
#     print(f'{image.GetSize()=}')
#     pixel_data = adjust_hu(sitk.GetArrayFromImage(image)) if ADJUST_WINDOW else sitk.GetArrayFromImage(image)
#     print(f"{pixel_data.shape=}")
#     noise_cancel_data = find_max_area(pixel_data)
#     for i in range(len(noise_cancel_data)):
#         noise_cancel_data[i] = np.where(noise_cancel_data[i] > 0, 1, 0)
#
#         plt.title(f"WW: {window_width}, WL: {window_level}")
#         plt.axis('off')
#         plt.imshow(noise_cancel_data[i], cmap=plt.cm.gray)
#         plt.show()


# def adjust_hu(image, ct_min=CT_min, ct_max=CT_max, ww=window_width):
#     """
#     Adjust the HU value of the image.
#     :param image:
#     :param ct_min:
#     :param ct_max:
#     :param ww:
#     :return: Adjusted image.
#     """
#     print(f' in adjust_hu() {ct_max=}, {ct_min=}, {ww=}')
#     adjusted_image = np.clip(image, ct_min, ct_max).astype(np.float32)
#     adjusted_image = (adjusted_image - ct_min) / ww * 255
#     adjusted_image = adjusted_image.astype(np.uint16)
#
#     return adjusted_image


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

    print(f'in resample_dicom() {original_spacing=}')
    print(f'in resample_dicom() {original_shape=}')
    print(f'in resample_dicom() {scaling_factors=}')
    print(f'in resample_dicom() {resample_image.GetSize()=}')
    print(f'in resample_dicom() {resample_image.GetSpacing()=}')
    print(f'in resample_dicom() {resample_image.GetOrigin()=}')
    print(f'in resample_dicom() {resample_image.GetDirection()=}')

    return sitk.GetArrayFromImage(resample_image)


# def merge_dicom(origin, mask) -> sitk.Image:
#     """
#     Merge the mask and the original image.
#     :param origin:
#     :param mask:
#     :return: The merged image.
#     """
#     mask = sitk.ReadImage(mask, sitk.sitkFloat32)
#     origin = sitk.ReadImage(origin, sitk.sitkFloat32)
#     mask = sitk.GetArrayFromImage(mask)
#     origin = sitk.GetArrayFromImage(origin)
#
#     # use opencv to merge two images
#     merged_dicom = cv2.bitwise_or(origin, mask)
#     merged_dicom = sitk.GetImageFromArray(merged_dicom.astype(np.uint16))
#
#     return merged_dicom


if __name__ == '__main__':
    dicom_dir = r"C:\Users\Hun\Desktop\127 test\BL"
    # dicom_dir = r"C:\Users\Hun\Desktop\127 test\FU"
    dicom2Dto3D(dicom_dir)
