
import os
import SimpleITK as sitk
import matplotlib.pyplot as plt

from natsort import natsorted


if __name__ == '__main__':
    dicom_dir = os.path.join(r"C:\Users\Hun\Desktop\127 test\FU")
    dicom_list = natsorted(os.listdir(dicom_dir))
    fu_image = sitk.ReadImage(os.path.join(dicom_dir, dicom_list[0]), sitk.sitkFloat32)
    print(f"{fu_image.GetSpacing()=}")
    print(f"{fu_image.GetDirection()=}")
    print(f"{fu_image.GetOrigin()=}")

    dicom_dir = os.path.join(r"C:\Users\Hun\Desktop\127 test\BL")
    dicom_list = natsorted(os.listdir(dicom_dir))
    bl_image = sitk.ReadImage(os.path.join(dicom_dir, dicom_list[0]), sitk.sitkFloat32)
    print(f"{bl_image.GetSpacing()=}")
    print(f"{bl_image.GetDirection()=}")
    print(f"{bl_image.GetOrigin()=}")

    # fu_image = sitk.GetArrayViewFromImage(fu_image)[0, :, :]
    # print(fu_image.shape)

    # 分開顯示兩張影像
    fig, axs = plt.subplots(1, 2)
    axs[0].imshow(sitk.GetArrayViewFromImage(fu_image)[0, :, :], cmap='gray')
    axs[0].set_title('fu_image')
    axs[1].imshow(sitk.GetArrayViewFromImage(bl_image)[0, :, :], cmap='gray')
    axs[1].set_title('bl_image')
    plt.show()
