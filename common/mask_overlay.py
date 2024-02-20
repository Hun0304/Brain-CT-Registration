"""
This file is used to visualize the registration result.
"""

import os
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt

from tqdm import tqdm
from datetime import date
from natsort import natsorted


def visualization(origin_dicom: str, regis_dicom: str, result_dir: str) -> None:
    """
    Visualize the registration result.
    :param origin_dicom: The baseline image.        Red channel.
    :param regis_dicom: The follow-up image.      Green channel.
    :param result_dir: The directory of the output images.
    :return: None
    """
    case_name = os.path.basename(origin_dicom)[:os.path.basename(origin_dicom).find("-")]
    origin = sitk.ReadImage(origin_dicom, sitk.sitkUInt16)
    regis = sitk.ReadImage(regis_dicom, sitk.sitkUInt16)
    interval = 6
    if origin.GetSize()[2] == regis.GetSize()[2]:
        regis.CopyInformation(origin)
    else:
        print(f"{case_name} has different size of images.")
        # 生成黑背景
        if origin.GetSize()[2] > regis.GetSize()[2]:
            zeros = sitk.Image(origin.GetSize(), origin.GetPixelID())
            zeros.CopyInformation(origin)
            # if origin.GetSize()[0] > regis.GetSize()[0]:
            #     #  clip the image
            #     for i in range(regis.GetSize()[0]):
            #         zeros[i, :, :] = regis[i, :, :]
            # elif origin.GetSize()[1] > regis.GetSize()[1]:
            #     for i in range(regis.GetSize()[1]):
            #         zeros[:, i, :] = regis[:, i, :]
            for i in range(regis.GetSize()[2]):
                zeros[:, :, i] = regis[:, :, i]
        else:
            zeros = sitk.Image(regis.GetSize(), regis.GetPixelID())
            zeros.CopyInformation(regis)
            for i in range(origin.GetSize()[2]):
                zeros[:, :, i] = origin[:, :, i]

        # print(f"origin size: {origin.GetSize()}")
        # print(f"zero size: {zeros.GetSize()}")
        # print(f"regis size: {regis.GetSize()}")
        # 用黑背景來補齊影像
        if origin.GetSize()[2] > regis.GetSize()[2]:
            regis = zeros
        else:
            origin = zeros

    # 計算需要創建多少個子圖
    total_slices = origin.GetSize()[2] if origin.GetSize()[2] < regis.GetSize()[2] else regis.GetSize()[2]
    num_subplots = total_slices // interval + 1

    for i in tqdm(range(num_subplots), desc=f"{case_name} is visualizing...", position=0):
        start_slice = i * interval
        end_slice = min((i + 1) * interval, total_slices)

        # 創建一張畫布
        fig, axs = plt.subplots(2, 3, figsize=(16, 12))
        fig.suptitle(f"{case_name}  Red: Origin BL, Green: Registered FU", fontsize=16)

        for j, ax in enumerate(axs.flat):
            slice_idx = start_slice + j
            if slice_idx < end_slice:
                dcmUint8 = sitk.Cast(
                    sitk.IntensityWindowing(origin[:, :, slice_idx], 0, 150),
                    sitk.sitkUInt8)
                _regis = sitk.GetArrayFromImage(regis)
                _regis = np.where(_regis > 0, 255, 0)
                _regis = sitk.GetImageFromArray(_regis)
                _regis.CopyInformation(regis)
                regisUint8 = sitk.Cast(
                    sitk.IntensityWindowing(_regis[:, :, slice_idx], 0, 205),
                    sitk.sitkUInt8)
                # 建立空白影像
                zeros = sitk.Image(dcmUint8.GetSize(), regisUint8.GetPixelID())
                zeros.CopyInformation(dcmUint8)
                # 合併影像
                rgb_image = sitk.Cast(sitk.Compose(dcmUint8, regisUint8, zeros), sitk.sitkVectorUInt8)
                ax.imshow(sitk.GetArrayViewFromImage(rgb_image))
                ax.set_title(f"Slice {slice_idx}")
            else:
                ax.axis("off")  # 如果切片不夠，關閉多餘的子圖

        plt.savefig(os.path.join(result_dir, f"overlay_{i + 1}.png"))
        fig.clf()
        plt.close(fig)
        # plt.show()

    return None


def mask_overlay(dcm, mask, dir_path) -> None:
    """
    Show the mask on the baseline image.
    :param dcm: The baseline image.
    :param mask: Follow-up mask.
    :param dir_path: The directory of the output images.
    :return: None
    """
    dcm_3d = sitk.ReadImage(dcm, sitk.sitkFloat32)
    mask_3d = sitk.ReadImage(mask, sitk.sitkFloat32)
    slices = dcm_3d.GetSize()[2] if dcm_3d.GetSize()[2] < mask_3d.GetSize()[2] else mask_3d.GetSize()[2]

    for i in tqdm(range(slices)):
        dcm_slice = dcm_3d[:, :, i]
        mask_slice = mask_3d[:, :, i]

        # 將像素值型態轉為 UInt8
        dcmUint8 = sitk.Cast(sitk.IntensityWindowing(dcm_slice, windowMinimum=-2, windowMaximum=150), sitk.sitkUInt8)
        maskUint8 = sitk.Cast(sitk.IntensityWindowing(mask_slice, windowMinimum=0, windowMaximum=205), sitk.sitkUInt8)
        # 建立空白影像
        zeros = sitk.Image(dcmUint8.GetSize(), maskUint8.GetPixelID())
        zeros.CopyInformation(dcmUint8)

        # 各種合併影像方式
        rgb_image1 = sitk.Cast(sitk.Compose(dcmUint8, maskUint8, zeros), sitk.sitkVectorUInt8)
        rgb_image2 = sitk.Cast(sitk.Compose(dcmUint8, maskUint8, dcmUint8), sitk.sitkVectorUInt8)
        rgb_image3 = sitk.Cast(sitk.Compose(dcmUint8, dcmUint8 * 0.5 + maskUint8 * 0.5, maskUint8),
                               sitk.sitkVectorUInt8)

        fig, axs = plt.subplots(2, 3, figsize=(16, 12))
        fig.suptitle(f"Slice {i}", fontsize=16)
        axs[0, 0].imshow(sitk.GetArrayViewFromImage(dcm_slice), cmap=plt.cm.gray)
        axs[0, 0].set_title('Baseline Original')
        axs[0, 1].imshow(sitk.GetArrayViewFromImage(mask_slice), cmap=plt.cm.gray)
        axs[0, 1].set_title('Follow-Up Mask')
        axs[0, 2].axis('off')

        axs[1, 0].imshow(sitk.GetArrayViewFromImage(rgb_image1))
        axs[1, 0].set_title('Red/Green')
        axs[1, 1].imshow(sitk.GetArrayViewFromImage(rgb_image2))
        axs[1, 1].set_title('Magenta/Green')
        axs[1, 2].imshow(sitk.GetArrayViewFromImage(rgb_image3))
        axs[1, 2].set_title('Orange/Blue')
        os.makedirs(dir_path, exist_ok=True)
        plt.savefig(os.path.join(dir_path, f"slice_{i}.png"))
        # plt.show()

    return None


def mask_overlay_main(dir_path: str, suffix=".dcm") -> None:
    """
    Main function.
    :return: None
    """
    case_list = natsorted(os.listdir(dir_path))
    with tqdm(total=len(case_list), position=0) as pbar:
        for case_name in case_list:
            pbar.set_description(f"{case_name} is visualizing...")
            result_path = os.path.join(dir_path, case_name, "result", "bl + regis mask overlay")
            reg_path = os.path.join(dir_path, case_name, "registration result")
            mask_path = os.path.join(dir_path, case_name, "mask", "result")
            dicom_path = os.path.join(dir_path, case_name, "dcm", "result")
            reg_ct = os.path.join(reg_path, f"registered-ct-2023-11-08{suffix}")
            # reg_mask = os.path.join(reg_path, f"registered-mask-2023-10-24{suffix}")
            reg_mask = os.path.join(reg_path, f"registered-mask-2023-11-08{suffix}")
            dicom_bl = os.path.join(dicom_path, f"{case_name}-1-brain-resample{suffix}")
            dicom_fu = os.path.join(dicom_path, f"{case_name}-2-brain-resample{suffix}")
            mask_bl = os.path.join(mask_path, f"{case_name}-1-mask-resample{suffix}")
            mask_fu = os.path.join(mask_path, f"{case_name}-2-mask-resample{suffix}")

            origin_mask_bl = os.path.join(mask_path, f"{case_name}-1-mask{suffix}")
            origin_dicom_bl = os.path.join(dir_path, case_name, "dcm", "result", f"{case_name}-1-brain-denoised{suffix}")
            origin_dicom_fu = os.path.join(dir_path, case_name, "dcm", "result", f"{case_name}-2-brain-denoised{suffix}")
            resample_back_mask = os.path.join(mask_path, f"{case_name}-registered-back-mask-2023-11-24{suffix}")

            os.makedirs(result_path, exist_ok=True)
            # if sitk.ReadImage(origin_dicom_bl, sitk.sitkFloat32).GetSize() != sitk.ReadImage(resample_back_mask, sitk.sitkFloat32).GetSize():
            #     print(f"{case_name} has different size of images.",
            #           sitk.ReadImage(origin_dicom_bl, sitk.sitkFloat32).GetSize(),
            #           sitk.ReadImage(resample_back_mask, sitk.sitkFloat32).GetSize())
            # else:
            visualization(origin_dicom_bl, resample_back_mask, result_path)
            pbar.update()
    return None
