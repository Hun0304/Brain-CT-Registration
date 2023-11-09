
import os

from common.globel_veriable import DATASETS_DIR_420, REGISTRATION_DIR_420, REGISTRATION_DIR_127
from datasets.ich420.resample import DICOM_Resample_ICH420, Mask_Resample_ICH420
from registration import registration_main
from common.mask_overlay import mask_overlay_main


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

    datasets_dicom_dir = os.path.join(DATASETS_DIR_420, "Images")
    datasets_mask_dir = os.path.join(DATASETS_DIR_420, "Labels")
    # DICOM_Resample_ICH420(datasets_dicom_dir)
    # Mask_Resample_ICH420(datasets_mask_dir)
    # registration_main(REGISTRATION_DIR_420, ".nii.gz")
    mask_overlay_main(REGISTRATION_DIR_420, ".nii.gz")
    # mask_overlay_main(REGISTRATION_DIR_127)


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
    # mask_overlay_main()

    # mask resample back
    # ------------------------------------- #
    # mask_resample_back()

    # get the meta data
    # ------------------------------------- #
    # case_list = natsorted(os.listdir(os.path.join(REGISTRATION_DIR_127)))
    # meta_datas = {}
    # no_mask_list = ["Case 25", "Case 70", "Case 156", "Case 299", "Case 319", "Case 327", "Case 329", "Case 337"]
    # json_file = os.path.abspath(os.path.join(REGISTRATION_DIR_127, "..", "127_meta_datas.json"))
    # with tqdm(total=len(case_list)) as pbar:
    #     for case in case_list:
    #         pbar.set_description(f"{case} is getting meta data...")
    #         if case in no_mask_list:
    #             pbar.update()
    #             continue
    #         dicom_bl_dir = os.path.join(REGISTRATION_DIR_127, case, "dcm", "BL")
    #         dicom_fu_dir = os.path.join(REGISTRATION_DIR_127, case, "dcm", "FU")
    #         _, meta_datas[f"{case}-1"] = get_meta_data(os.path.join(dicom_bl_dir, f"{case}-1-1.dcm"))
    #         _, meta_datas[f"{case}-2"] = get_meta_data(os.path.join(dicom_fu_dir, f"{case}-2-1.dcm"))
    #         pbar.update()
    # print(meta_datas)
    # with open(json_file, "w") as f:
    #     json.dump(meta_datas, f)

    # write to excel
    # ------------------------------------- #
    # write2excel()


if __name__ == '__main__':
    main()
