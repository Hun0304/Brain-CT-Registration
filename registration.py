
import os
import json
import numpy as np
import SimpleITK as sitk

from tqdm import tqdm
from typing import Tuple
from natsort import natsorted
from datetime import date


def registration(fixed_image, moving_image, mask=False, multi_model=False) -> Tuple[sitk.VersorRigid3DTransform, float]:
    """
    # Registration
    :param fixed_image: baseline image
    :param moving_image: follow-up image
    :param mask: whether to use mask
    :param multi_model: whether to use multi-model ex: ct & mri
    :return: final_transform
    """
    interpolator = sitk.sitkNearestNeighbor if mask else sitk.sitkLinear

    registration_method = sitk.ImageRegistrationMethod()
    if multi_model:
        registration_method.SetMetricAsMattesMutualInformation()
    else:
        registration_method.SetMetricAsCorrelation()

    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)
    registration_method.SetInterpolator(interpolator)
    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0,
                                                      numberOfIterations=1000,
                                                      convergenceMinimumValue=1e-6,
                                                      convergenceWindowSize=10)
    registration_method.SetOptimizerScalesFromPhysicalShift()
    initial_transform = sitk.CenteredTransformInitializer(fixed_image,
                                                          moving_image,
                                                          sitk.VersorRigid3DTransform(),
                                                          # sitk.Euler3DTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)
    registration_method.SetInitialTransform(initial_transform, inPlace=False)
    final_transform = registration_method.Execute(fixed_image, moving_image)
    print(f"Final metric value: {registration_method.GetMetricValue()}")
    print(f"Optimizer's stopping condition, {registration_method.GetOptimizerStopConditionDescription()}")
    print(f"Final transform parameters: {final_transform.GetParameters()}")

    return final_transform, registration_method.GetMetricValue()


def registration_mask(mask_3d: sitk.Image, mask_bl: sitk.Image, tfm: sitk.VersorRigid3DTransform, result_dir: str, suffix=".dcm") -> None:
    """
    # Using transform to 3d mask
    :param mask_3d: 3D mask
    :param mask_bl: baseline image mask
    :param tfm: transform
    :param result_dir: result directory
    :param suffix: file suffix
    :return: None
    """
    registered_mask_3d = sitk.Resample(mask_3d, mask_bl, tfm, sitk.sitkNearestNeighbor, 0.0, mask_3d.GetPixelID())
    registered_mask_3d = sitk.Cast(registered_mask_3d, sitk.sitkUInt16)
    registered_mask_3d = sitk.GetArrayFromImage(registered_mask_3d)
    registered_mask_3d = np.where(registered_mask_3d > 0, 255, 0)
    registered_mask_3d = sitk.GetImageFromArray(registered_mask_3d)
    registered_mask_3d = sitk.Cast(registered_mask_3d, sitk.sitkUInt16)
    registered_mask_3d.CopyInformation(mask_bl)

    sitk.WriteImage(registered_mask_3d, os.path.join(result_dir, f"registered-mask-{date.today()}{suffix}"))
    return None


def registration_main(dir_path: str, suffix=".dcm"):
    """
    Main function.
    """
    metric_value_dict = {}
    case_dir = natsorted(os.listdir(dir_path))

    with tqdm(total=len(case_dir)) as pbar:
        for case_name in case_dir:
            pbar.set_description(f"{case_name} is registering...")
            reg_flag = True
            reg_path = os.path.join(dir_path, case_name, "registration result")
            dicom_path = os.path.join(dir_path, case_name, "dcm", "result")
            mask_path = os.path.join(dir_path, case_name, "mask", "result")

            def check_file(file_path: str, file_type: str):
                """
                Check the file exists or not.
                :param file_path: The file path.
                :param file_type: The file type.
                :return: The file.
                """
                nonlocal reg_flag
                if os.path.exists(file_path):
                    return sitk.ReadImage(file_path, sitk.sitkFloat32)
                else:
                    reg_flag = False
                    print(f"{case_name} has no {file_type}")
                    return None

            bone_image_bl = check_file(os.path.join(dicom_path, f"{case_name}-1-bone-resample{suffix}"),
                                       "BL bone resample dicom")
            bone_image_fu = check_file(os.path.join(dicom_path, f"{case_name}-2-bone-resample{suffix}"),
                                       "FU bone resample dicom")
            brain_image_bl = check_file(os.path.join(dicom_path, f"{case_name}-1-brain-resample{suffix}"),
                                        "BL brain resample dicom")
            brain_image_fu = check_file(os.path.join(dicom_path, f"{case_name}-2-brain-resample{suffix}"),
                                        "FU brain resample dicom")
            mask_image_bl = check_file(os.path.join(mask_path, f"{case_name}-1-mask-resample{suffix}"),
                                       "BL mask")
            mask_image_fu = check_file(os.path.join(mask_path, f"{case_name}-2-mask-resample{suffix}"),
                                       "FU mask")

            if reg_flag:
                transform_dcm, metric_value = registration(brain_image_bl, brain_image_fu)
                metric_value_dict[case_name] = metric_value
                registered_dcm = sitk.Resample(brain_image_fu, brain_image_bl, transform_dcm, sitk.sitkLinear, 0.0,
                                               brain_image_fu.GetPixelID())
                registered_dcm.CopyInformation(mask_image_bl)
                registered_dcm = sitk.Cast(registered_dcm, sitk.sitkUInt16)
                os.makedirs(reg_path, exist_ok=True)
                sitk.WriteImage(registered_dcm, os.path.join(reg_path, f"registered-ct-{date.today()}{suffix}"))
                sitk.WriteTransform(transform_dcm, os.path.join(reg_path, f"registered-ct-tf-{date.today()}.tfm"))

                registration_mask(mask_image_fu, mask_image_bl, transform_dcm, reg_path, suffix)
            pbar.update()
    dataset_name = dir_path.split(os.sep)[-1]
    with open(os.path.abspath(os.path.join(dir_path, "..", f"{dataset_name}_metric_value.json")), "w") as f:
        json.dump(metric_value_dict, f)

    print(metric_value_dict)
    print(sorted(metric_value_dict.values()))
    print(sorted(metric_value_dict, key=metric_value_dict.get))
    print(f"Best case: {sorted(metric_value_dict, key=metric_value_dict.get)[0]}")
    print(f"Worst case: {sorted(metric_value_dict, key=metric_value_dict.get)[-1]}")
    return None
