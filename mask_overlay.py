
import os
import SimpleITK as sitk
import matplotlib.pyplot as plt

from tqdm import tqdm


def mask_overlay(dcm, mask) -> None:
    """
    Show the mask on the baseline image.
    :param dcm: The baseline image.
    :param mask: Follow-up mask.
    :return: None
    """
    dcms = sitk.ReadImage(dcm, sitk.sitkFloat32)
    masks = sitk.ReadImage(mask, sitk.sitkFloat32)
    slices = dcms.GetSize()[2] if dcms.GetSize()[2] < masks.GetSize()[2] else masks.GetSize()[2]

    for i in tqdm(range(slices)):
        dcms_slice = dcms[:, :, i]
        masks_slice = masks[:, :, i]

        # 將像素值型態轉為 UInt8
        dcmUint8 = sitk.Cast(sitk.IntensityWindowing(dcms_slice, windowMinimum=-2, windowMaximum=150), sitk.sitkUInt8)
        maskUint8 = sitk.Cast(sitk.IntensityWindowing(masks_slice, windowMinimum=0, windowMaximum=205), sitk.sitkUInt8)
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
        axs[0, 0].imshow(sitk.GetArrayViewFromImage(dcms_slice), cmap=plt.cm.gray)
        axs[0, 0].set_title('Baseline Original')
        axs[0, 1].imshow(sitk.GetArrayViewFromImage(masks_slice), cmap=plt.cm.gray)
        axs[0, 1].set_title('Follow-Up Mask')
        axs[0, 2].axis('off')

        axs[1, 0].imshow(sitk.GetArrayViewFromImage(rgb_image1))
        axs[1, 0].set_title('Red/Green')
        axs[1, 1].imshow(sitk.GetArrayViewFromImage(rgb_image2))
        axs[1, 1].set_title('Magenta/Green')
        axs[1, 2].imshow(sitk.GetArrayViewFromImage(rgb_image3))
        axs[1, 2].set_title('Orange/Blue')
        dir_path = r"C:\Users\Hun\Desktop\127 test\result_0914"
        os.makedirs(dir_path, exist_ok=True)
        plt.savefig(os.path.join(dir_path, f"slice_{i}.png"))
        plt.show()

    return None


if __name__ == '__main__':
    dicom = r"C:\Users\Hun\Desktop\127 test\new_0825\Case 1-1_brain_resample.dcm"
    mask = r"C:\Users\Hun\Desktop\127 test\new_0825\registration\registered_mask_0914.dcm"
    registered_ct = r"C:\Users\Hun\Desktop\127 test\new_0825\registration\registered_ct_0914.dcm"
    # mask = r"C:\Users\Hun\Desktop\127 test\mask_overlay_to_baseline_0825.dcm"
    # mask = r"C:\Users\Hun\Desktop\127 test\FU_Mask\Case 1-2-mask-resample.dcm"
    mask_overlay(dicom, mask)
