
import os
import random
import SimpleITK as sitk
import glob2
import numpy as np
import matplotlib.pyplot as plt

from tqdm import tqdm
from glob2 import glob
from natsort import natsorted
from shutil import copy2

from common.output import write_metric_value_2_excel, visualization_hist, write_metadata_2_excel, write_metadata_2_json
from common.mask_overlay import mask_overlay_main
from common.globel_veriable import DATASETS_DIR_420, REGISTRATION_DIR_420, REGISTRATION_DIR_127
from datasets.ich420.resample import DICOM_Resample_ICH420, Mask_Resample_ICH420
from datasets.ich127.resample import DICOM_Resample_ICH127, Mask_Resample_ICH127, Mask_Resample_Back_ICH127
from registration import registration_main, registration
from medical.utils import get_meta_data, calc_correlation, dicom2Dto3D
from mask_Resample import mask_resample_back


# from mask_overlay import mask_overlay_main


def main():
    """
    Main function.
    """

    # datasets preprocess
    # ------------------------------------- #
    # datasets_dicom_dir = os.path.join(DATASETS_DIR_127, "Images")
    # datasets_mask_dir = os.path.join(DATASETS_DIR_127, "Labels")
    # datasets_dicom_dir_bl = os.path.join(datasets_dicom_dir, "BL CT")
    # datasets_dicom_dir_fu = os.path.join(datasets_dicom_dir, "FU CT")
    # datasets_mask_dir_bl = os.path.join(datasets_mask_dir, "BL CT")
    # datasets_mask_dir_fu = os.path.join(datasets_mask_dir, "FU CT")
    # preprocess_127_dir(datasets_dicom_dir_bl)
    # preprocess_127_dir(datasets_dicom_dir_fu)
    # preprocess_127_dir(datasets_mask_dir_bl)
    # preprocess_127_dir(datasets_mask_dir_fu)

    # datasets_dicom_dir = os.path.join(DATASETS_DIR_420, "Images")
    # datasets_mask_dir = os.path.join(DATASETS_DIR_420, "Labels")
    # DICOM_Resample_ICH420(datasets_dicom_dir)
    # Mask_Resample_ICH420(datasets_mask_dir)
    # registration_main(REGISTRATION_DIR_420, ".nii.gz")
    # mask_overlay_main(REGISTRATION_DIR_420, ".nii.gz")
    # mask_overlay_main(REGISTRATION_DIR_127)
    # write2excel(REGISTRATION_DIR_420)


    # resample 3D
    # ------------------------------------- #
    # case_list = natsorted(os.listdir(os.path.join(REGISTRATION_DIR_127)))
    # no_mask_list = ["Case 25", "Case 70", "Case 156", "Case 299", "Case 319", "Case 327", "Case 329", "Case 337"]
    # with tqdm(total=len(case_list)) as pbar:
    #     for case in case_list:
    #         pbar.set_description(f"{case} 3D Resampling...")
    #         dicom_bl_dir = os.path.join(REGISTRATION_DIR_127, case, "dcm", "BL")
    #         dicom_fu_dir = os.path.join(REGISTRATION_DIR_127, case, "dcm", "FU")
    #         mask_bl_dir = os.path.join(REGISTRATION_DIR_127, case, "mask", "BL")
    #         mask_fu_dir = os.path.join(REGISTRATION_DIR_127, case, "mask", "FU")
    #         dicom2Dto3D(dicom_bl_dir)
    #         dicom2Dto3D(dicom_fu_dir)
    #         if case in no_mask_list:
    #             pbar.update()
    #             continue
    #         mask2Dto3D(mask_bl_dir, dicom_bl_dir)
    #         mask2Dto3D(mask_fu_dir, dicom_fu_dir)
    #         pbar.update()

    # ------------------------------------- #
    # Registration
    # registration_main()

    # ------------------------------------- #
    # Calculate the correlation
    # dict_values = {}
    # case_files = natsorted(os.listdir(os.path.join(REGISTRATION_DIR_127)))
    # problem_list = ["Case 25", "Case 70", "Case 156", "Case 157", "Case 177", "Case 221", "Case 246", "Case 274", "Case 295", "Case 299", "Case 319", "Case 327", "Case 329", "Case 337"]
    # for case in case_files:
    #     if case in problem_list:
    #         continue
    #     image_bl = os.path.join(REGISTRATION_DIR_127, case, "dcm", "result", f"{case}-1-bone-resample.dcm")
    #     image_fu = os.path.join(REGISTRATION_DIR_127, case, "registration result", "registered-ct-2023-10-18.dcm")
    #     dict_values[CASE_NAME] = calc_correlation(image_bl, image_fu)
    # print(dict_values)
    # print(f"Best case: {sorted(dict_values, key=dict_values.get)[0]}")
    # print(f"Worst case: {sorted(dict_values, key=dict_values.get)[-1]}")

    # visualization the histogram of the metric value
    # ------------------------------------- #
    # visualization_hist(os.path.abspath(os.path.join(REGISTRATION_DIR_127, "..", "127_metric_value.json")))

    # Calculate the hausdorff distance
    # ------------------------------------- #
    # case_files = natsorted(os.listdir(os.path.join(REGISTRATION_DIR_127)))
    # problem_list = ["Case 25", "Case 70", "Case 156", "Case 157", "Case 177", "Case 221", "Case 246", "Case 274", "Case 295", "Case 299", "Case 319", "Case 327", "Case 329", "Case 337"]
    # for case in case_files[:5]:
    #     if case in problem_list:
    #         continue
    #     image_bl = os.path.join(REGISTRATION_DIR_127, case, "dcm", "result", f"{case}-1-bone-resample.dcm")
    #     # image_fu = os.path.join(REGISTRATION_DIR_127, case, "dcm", "result", f"{case}-2-bone-resample.dcm")
    #     image_reg = os.path.join(REGISTRATION_DIR_127, case, "registration result", "registered-ct-2023-10-18.dcm")
    #     bl = sitk.ReadImage(image_bl, sitk.sitkFloat32)
    #     # fu = sitk.ReadImage(image_fu, sitk.sitkFloat32)
    #     reg = sitk.ReadImage(image_reg, sitk.sitkFloat32)
    #     metric_main(bl, reg)

    # overlay the mask on the CT
    # ------------------------------------- #
    # mask_overlay_main(REGISTRATION_DIR_420, ".nii.gz")

    # mask resample back
    # ------------------------------------- #
    # mask_resample_back()

    # get the meta data 420
    # --------------------------------------#
    # 420 沒有 manufacturer_tag


    # with open(json_file, "w") as f:
    #     json.dump(meta_datas, f)



    # write to excel
    # ------------------------------------- #
    # write2excel(REGISTRATION_DIR_420)
    # visualization_hist(os.path.abspath(os.path.join(REGISTRATION_DIR_420, "..", "ICH_420_metric_value.json")))

    # calculate the correlation
    # ------------------------------------- #
    # img_1 = os.path.join(REGISTRATION_DIR_420, "Spon Case 116", "dcm", "result", "Spon Case 116-1-brain-resample.nii.gz")
    # img_2 = os.path.join(REGISTRATION_DIR_420, "Spon Case 116", "registration result", "registered-ct-2023-11-08.nii.gz")
    # calc_correlation(img_1, img_2)

    # dicom 2d to 3d

    # dicom2Dto3D(r"D:\MS\TRC-LAB\ICH Project\Registration\ICH_420\Spon Case 366\dcm\BL")
    # img_420 = sitk.ReadImage(r"D:\MS\TRC-LAB\ICH Project\Registration\ICH_420\Case 1\dcm\BL\AN_ID_20200528121622@Case_1-1@1_Brain_routine@@20130926222448@SE2_Tilt_1.nii.gz")
    # img_127 = sitk.ReadImage(r"D:\MS\TRC-LAB\ICH Project\Registration\ICH_127\Case 1\dcm\BL\Case 1-1-1.dcm")
    # img_127_2 = sitk.ReadImage(r"D:\MS\TRC-LAB\ICH Project\Registration\ICH_127\Case 1\dcm\FU\Case 1-2-1.dcm")
    # print(get_meta_data(r"D:\MS\TRC-LAB\ICH Project\Registration\ICH_420\Spon Case 366\dcm\BL\Case 366_BL_0.dcm"))
    # print(img_127.GetSpacing(), img_127.GetOrigin(), img_127.GetDirection())
    # print(img_127_2.GetSpacing(), img_127_2.GetOrigin(), img_127_2.GetDirection())
    # print(get_meta_data(r"D:\MS\TRC-LAB\ICH Project\Registration\ICH_127\Case 1\dcm\BL\Case 1-1-1.dcm"))
    # print(get_meta_data("D:\MS\TRC-LAB\ICH Project\Registration\ICH_420\Case 1\dcm\BL\AN_ID_20200528121622@Case_1-1@1_Brain_routine@@20130926222448@SE2_Tilt_1.nii.gz"))
    # print(get_meta_data(r"D:\MS\TRC-LAB\ICH Project\Registration\ICH_420\Case 1\dcm\BL\AN_ID_20200528121622@Case_1-1@1_Brain_routine@@20130926222448@SE2_Tilt_1.nii.gz"))

    # write_metadata_2_json(REGISTRATION_DIR_127)
    # write_metadata_2_excel(REGISTRATION_DIR_127)

    # compare the metadata
    # ------------------------------------- #
    # nii_list = natsorted(glob(os.path.join(REGISTRATION_DIR_420, "**", "AN_ID*.nii.gz"), recursive=True))
    # patient_ids = []
    # for nii_file in nii_list:
    #     info = [os.path.basename(nii_file).split("@")[0], os.path.basename(nii_file).split("@")[1].split("@")[0]]
    #     patient_ids.append(info)
    # case_list = natsorted(os.listdir(REGISTRATION_DIR_127))
    # with open(os.path.abspath(os.path.join(REGISTRATION_DIR_420, "..", "ICH_127_metadata.json")), "r+") as f:
    #     meta_data = json.load(f)
    # for case in case_list:
    #     case = f"{case}-2"
    #     for patient_id in patient_ids:
    #         if patient_id[0] in meta_data[case]:
    #             print(case, patient_id)
    #             break

    # dataset_127 = r"D:\MS\TRC-LAB\ICH Datasets\ICH_127_Before"
    # case_list = natsorted(os.listdir(REGISTRATION_DIR_127))
    # for case in case_list:
    #     print(case)
    # ivh_list = natsorted(glob(os.path.join(dataset_127, "**", "*V*.tif"), recursive=True))
    # ivh_case_list = natsorted(set([os.path.basename(ivh)[:os.path.basename(ivh).find("-")+2] for ivh in ivh_list]))
    # for ivh_case in ivh_case_list:
    #     print(ivh_case)

    # DICOM_Resample_ICH127(REGISTRATION_DIR_127)
    # Mask_Resample_ICH127(REGISTRATION_DIR_127)
    # registration_main(REGISTRATION_DIR_127)
    # case_name = "Case 90"
    # case_list = natsorted(os.listdir(REGISTRATION_DIR_127))
    # for case_name in case_list:
    #     print(case_name)
    # img1 = fr"D:\MS\TRC-LAB\ICH Project\Registration\ICH_127\{case_name}\dcm\result\{case_name}-1-brain-resample.dcm"
    # img2 = fr"D:\MS\TRC-LAB\ICH Project\Registration\ICH_420\{case_name}\dcm\result\{case_name}-1-brain-resample.nii.gz"
    # img1 = sitk.ReadImage(img1, sitk.sitkFloat32)
    # img2 = sitk.ReadImage(img2, sitk.sitkFloat32)
    # registration(img1, img2)

    #----------------------------------------#

    # Mask_Resample_Back_ICH127(REGISTRATION_DIR_127)
    # case_list = natsorted(os.listdir(REGISTRATION_DIR_420))

    # for case in case_list:
    #     if case != "Spon Case 278":
    #         dicom_list.append(os.path.join(REGISTRATION_DIR_420, case, "dcm", "result", f"{case}-1-brain-denoised.nii.gz"))

    # dicom_list = [os.path.join(REGISTRATION_DIR_420, case, "dcm", "result", f"{case}-1-brain-denoised.nii.gz") for case in case_list]
    # mask_list = [os.path.join(REGISTRATION_DIR_420, case, "mask", "result", f"{case}-registered-back-mask-2023-11-24.nii.gz") for case in case_list]

    # for mask in mask_list:
    #     # print(mask)
    #     # case = os.path.join(os.path.dirname(mask), os.path.basename(mask)[:os.path.basename(mask).find("-")])
    #     dir = os.path.dirname(mask)
    #     basename = os.path.basename(mask)
    #     case = dir.split(os.sep)[-3]
    #     new_name = os.path.join(dir, f"{case}-{basename}")
    #     # print(f"{case}-{mask}")
    #     os.rename(mask, new_name)


    # image_dir = r"D:\MS\TRC-LAB\ICH Project\Registration\Images"
    # mask_dir = r"D:\MS\TRC-LAB\ICH Project\Registration\Labels"
    # combined_list = list(zip(dicom_list, mask_list))
    # print(combined_list[:10])

    # name_list = [(os.path.basename(dicom), os.path.basename(mask)) for dicom, mask in combined_list]
    # train_list = random.sample(name_list, int(len(name_list)*0.8))
    # test_list = [name for name in name_list if name not in train_list]
    #
    # os.makedirs(r"D:\MS\TRC-LAB\ICH Project\Registration\420_Train\Images", exist_ok=True)
    # os.makedirs(r"D:\MS\TRC-LAB\ICH Project\Registration\420_Train\Labels", exist_ok=True)
    # os.makedirs(r"D:\MS\TRC-LAB\ICH Project\Registration\420_Test\Images", exist_ok=True)
    # os.makedirs(r"D:\MS\TRC-LAB\ICH Project\Registration\420_Test\Labels", exist_ok=True)
    #
    # for train in train_list:
    #     case = train[0][:train[0].find("-")]
    #     dcm_path = os.path.join(REGISTRATION_DIR_420, case, "dcm", "result", train[0])
    #     # image = sitk.ReadImage(dcm_path, sitk.sitkFloat32)
    #     mask_path = os.path.join(REGISTRATION_DIR_420, case, "mask", "result", train[1])
    #     # mask = sitk.ReadImage(mask_path, sitk.sitkFloat32)
    #     # print(image.GetSize(), mask.GetSize())
    #     copy2(dcm_path, r"D:\MS\TRC-LAB\ICH Project\Registration\420_Train\Images")
    #     copy2(mask_path, r"D:\MS\TRC-LAB\ICH Project\Registration\420_Train\Labels")
    #     print(train.__str__().replace("'", "").replace("(", "").replace(")", "").replace(", ", ","))
    #
    # print("====================================" * 2)
    #
    #
    # for test in test_list:
    #     case = test[0][:test[0].find("-")]
    #     dcm_path = os.path.join(REGISTRATION_DIR_420, case, "dcm", "result", test[0])
    #     # image = sitk.ReadImage(dcm_path, sitk.sitkFloat32)
    #     mask_path = os.path.join(REGISTRATION_DIR_420, case, "mask", "result", test[1])
    #     # mask = sitk.ReadImage(mask_path, sitk.sitkFloat32)
    #     # print(image.GetSize(), mask.GetSize())
    #     copy2(dcm_path, r"D:\MS\TRC-LAB\ICH Project\Registration\420_Test\Images")
    #     copy2(mask_path, r"D:\MS\TRC-LAB\ICH Project\Registration\420_Test\Labels")
    #     print(test.__str__().replace("'", "").replace("(", "").replace(")", "").replace(", ", ","))
    #
    # # for train in train_list:
    # #     image = sitk.ReadImage(train)
    # #     print(train, image.GetSize())
    # # print("====================================")
    # # for test in test_list:
    # #     print(test)
    # mask_overlay_main(REGISTRATION_DIR_420, suffix=".nii.gz")

    # path = r"D:\MS\TRC-LAB\ICH Project\Registration\expended_image"
    # os.makedirs(path, exist_ok=True)
    # case_list = natsorted(os.listdir(REGISTRATION_DIR_420))
    # dicom_list = [os.path.join(REGISTRATION_DIR_420, case, "dcm", "result", f"{case}-1-brain-denoised.nii.gz") for case in case_list]
    # mask_list = [os.path.join(REGISTRATION_DIR_420, case, "mask", "result", f"{case}-registered-back-mask-2023-11-24.nii.gz") for case in case_list]
    # for dcm, mask in tqdm(zip(dicom_list, mask_list), total=len(dicom_list)):
    #     case = os.path.basename(dcm)[:os.path.basename(dcm).find("-")]
    #     image = sitk.ReadImage(dcm)
    #     image_array = sitk.GetArrayFromImage(image).T
    #     mask = sitk.ReadImage(mask)
    #     mask_array = sitk.GetArrayFromImage(mask).T
    #
    #     # expend to 768 * 768 * slices
    #     expend_image_array = np.zeros((768, 768, image_array.shape[2]), dtype=np.float32)
    #     expend_mask_array = np.zeros((768, 768, mask_array.shape[2]), dtype=np.uint16)
    #     x_center = image_array.shape[0] // 2
    #     y_center = image_array.shape[1] // 2
    #     if image_array.shape[1] % 2 == 0:
    #         expend_image_array[384-x_center:384+x_center, 384-y_center:384+y_center, :] = image_array
    #         expend_mask_array[384-x_center:384+x_center, 384-y_center:384+y_center, :] = mask_array
    #     else:
    #         expend_image_array[384-x_center:384+x_center, 384-y_center-1:384+y_center, :] = image_array
    #         expend_mask_array[384-x_center:384+x_center, 384-y_center-1:384+y_center, :] = mask_array
    #     expend_image = sitk.GetImageFromArray(expend_image_array.T)
    #     expend_mask = sitk.GetImageFromArray(expend_mask_array.T)
    #     sitk.WriteImage(expend_image, os.path.join(path, "dcm", f"{case}-1-brain-denoised.nii.gz"))
    #     sitk.WriteImage(expend_mask, os.path.join(path, "mask", f"{case}-registered-back-mask-2023-11-24.nii.gz"))

    # case_list = natsorted(os.listdir(REGISTRATION_DIR_420))
    # dicom_list = [os.path.join(REGISTRATION_DIR_420, case, "dcm", "result", f"{case}-2-brain-denoised.nii.gz") for case in case_list]
    # mask_list = [os.path.join(REGISTRATION_DIR_420, case, "mask", "result", f"{case}-2-mask") for case in case_list]
    #
    # for dcm, mask in tqdm(zip(dicom_list, mask_list), total=len(dicom_list)):
    #     image = sitk.ReadImage(dcm)
    #     mask = sitk.ReadImage(mask)
    #     image_array = sitk.GetArrayFromImage(image).T
    #     mask_array = sitk.GetArrayFromImage(mask).T
    #     for i in range(mask_array.shape[2]):
    #         if mask_array[:, :, i].sum() > 0:
    #             fig, axs = plt.subplots(1, 2, figsize=(12, 8))
    #             fig.suptitle(f"{os.path.basename(dcm)}", fontsize=16)
    #             axs[0].imshow(image_array[:, :, i].T, cmap=plt.cm.gray)
    #             axs[0].set_title(f"Slice {i}")
    #             axs[1].imshow(mask_array[:, :, i].T, cmap=plt.cm.gray)
    #             axs[1].set_title(f"Slice {i}")
    #             plt.savefig(os.path.join(r"D:\MS\TRC-LAB\ICH Project\Registration\check_ivh\FU", f"{os.path.basename(dcm).split('.nii.gz')[0].split('-brain-denoised')[0]}-{i}-check.png"))
    #             fig.clf()
    #             plt.close(fig)

    registered_mask_list = natsorted(glob2.glob(os.path.join(r"D:\MS\TRC-LAB\ICH Project\Registration\expended_image\_mask", "**", "*-registered-back-mask-2023-11-24.nii.gz"), recursive=True))
    for mask in tqdm(registered_mask_list):
        mask_image = sitk.ReadImage(mask)
        mask_array = sitk.GetArrayFromImage(mask_image)
        if mask_array.sum() != 0:
            #  pixel value 255 to 1
            mask_array = np.where(mask_array > 0, 1, 0)
        mask_image = sitk.GetImageFromArray(mask_array)
        mask_image.CopyInformation(mask_image)
        sitk.WriteImage(mask_image, os.path.join(rf"D:\MS\TRC-LAB\ICH Project\Registration\420_labels_1\{os.path.basename(mask)}"))

    return None


if __name__ == '__main__':
    main()

