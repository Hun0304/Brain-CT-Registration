
import os
import SimpleITK as sitk
import matplotlib.pyplot as plt

from tqdm import tqdm
from datetime import date
from natsort import natsorted

from globel_veriable import REGISTRATION_DIR_127


def visualization(origin_dicom: str, regis_dicom: str, result_dir: str) -> None:
    """
    Visualize the registration result.
    :param origin_dicom: The baseline image.   Red channel.
    :param regis_dicom: The follow-up image.      Green channel.
    :param result_dir: The directory of the output images.
    :return: None
    """
    case_name = os.path.basename(regis_dicom)[:os.path.basename(origin_dicom).find("-")]
    case_name = case_name[:case_name.rfind("-")]
    origin = sitk.ReadImage(origin_dicom, sitk.sitkFloat32)
    regis = sitk.ReadImage(regis_dicom, sitk.sitkFloat32)
    interval = 6

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
                    sitk.IntensityWindowing(origin[:, :, slice_idx], windowMinimum=-2, windowMaximum=150),
                    sitk.sitkUInt8)
                regisUint8 = sitk.Cast(
                    sitk.IntensityWindowing(regis[:, :, slice_idx], windowMinimum=0, windowMaximum=205),
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

        plt.savefig(os.path.join(result_dir, f"result_{i + 1}.png"))
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


def mask_overlay_main() -> None:
    """
    Main function.
    :return:
    """
    no_mask_list = ["Case 25", "Case 70", "Case 156", "Case 299", "Case 319", "Case 327", "Case 329", "Case 337"]
    case_list = natsorted(os.listdir(REGISTRATION_DIR_127))
    with tqdm(total=len(case_list)) as pbar:
        for case_name in case_list:
            pbar.set_description(f"{case_name} is visualizing...")
            if case_name in no_mask_list:
                pbar.update()
                continue
            result_path = os.path.join(REGISTRATION_DIR_127, case_name, "result")
            reg_path = os.path.join(REGISTRATION_DIR_127, case_name, "registration result")
            mask_path = os.path.join(REGISTRATION_DIR_127, case_name, "mask", "result")
            dicom_path = os.path.join(REGISTRATION_DIR_127, case_name, "dcm", "result")
            reg_ct = os.path.join(reg_path, f"registered-ct-{date.today()}.dcm")
            reg_mask = os.path.join(reg_path, f"registered-mask-{date.today()}.dcm")
            dicom_bl = os.path.join(dicom_path, f"{case_name}-1-brain-resample.dcm")
            dicom_fu = os.path.join(dicom_path, f"{case_name}-2-brain-resample.dcm")
            mask_bl = os.path.join(mask_path, f"{case_name}-1-mask-resample.dcm")
            mask_fu = os.path.join(mask_path, f"{case_name}-2-mask-resample.dcm")
            os.makedirs(result_path, exist_ok=True)
            visualization(reg_mask, mask_bl, result_path)
            pbar.update()
