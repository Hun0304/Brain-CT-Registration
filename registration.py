
import os
import SimpleITK as sitk

from DICOM_Resample import case_dir, case_name
from datetime import date


def registration(fixed_image, moving_image, mask=False) -> sitk.Euler3DTransform:
    """
    # Registration
    :param fixed_image: baseline image
    :param moving_image: follow-up image
    :param mask: whether to use mask
    :return: final_transform
    """
    interpolator = sitk.sitkNearestNeighbor if mask else sitk.sitkLinear

    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation()
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)
    registration_method.SetInterpolator(interpolator)
    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0,
                                                      numberOfIterations=100,
                                                      convergenceMinimumValue=1e-6,
                                                      convergenceWindowSize=10)
    registration_method.SetOptimizerScalesFromPhysicalShift()
    initial_transform = sitk.CenteredTransformInitializer(fixed_image,
                                                          moving_image,
                                                          sitk.Euler3DTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)
    registration_method.SetInitialTransform(initial_transform, inPlace=False)
    final_transform = registration_method.Execute(fixed_image, moving_image)
    return final_transform


def registration_mask(mask_3d, bl, tfm: sitk.Euler3DTransform, result_dir) -> None:
    """
    # Using transform to 3d mask
    :param mask_3d: 3D mask
    :param bl: baseline image
    :param tfm: transform
    :param result_dir: result directory
    :return: None
    """
    registered_mask_3d = sitk.Resample(mask_3d, tfm, sitk.sitkNearestNeighbor, 0.0, mask_3d.GetPixelID())
    registered_mask_3d = sitk.Cast(registered_mask_3d, sitk.sitkUInt16)
    print(f"{bl.GetSize()=}")
    print(f"{mask_3d.GetSize()=}")
    print(f"{registered_mask_3d.GetSize()=}")
    print(f"{registered_mask_3d.GetSpacing()=}")
    print(f"{registered_mask_3d.GetOrigin()=}")
    print(f"{registered_mask_3d.GetDirection()=}")
    sitk.WriteImage(registered_mask_3d, os.path.join(result_dir, f"registered-mask-{date.today()}.dcm"))
    return None


if __name__ == '__main__':
    reg_path = os.path.join(case_dir, "registration")
    dicom_path = os.path.join(case_dir, "dcm", "result")
    mask_path = os.path.join(case_dir, "mask", "result")
    bone_dicom_bl = os.path.join(dicom_path, case_name + "-1-bone-resample.dcm")
    bone_dicom_fu = os.path.join(dicom_path, case_name + "-2-bone-resample.dcm")
    brain_dicom_bl = os.path.join(dicom_path, case_name + "-1-brain-resample.dcm")
    brain_dicom_fu = os.path.join(dicom_path, case_name + "-2-brain-resample.dcm")
    # mask_dicom_bl = os.path.join(mask_path, case_name + "-1-mask-resample.dcm")
    mask_dicom_fu = os.path.join(mask_path, case_name + "-2-mask-resample.dcm")
    bone_image_bl = sitk.ReadImage(bone_dicom_bl, sitk.sitkFloat32)
    bone_image_fu = sitk.ReadImage(bone_dicom_fu, sitk.sitkFloat32)
    brain_image_bl = sitk.ReadImage(brain_dicom_bl, sitk.sitkFloat32)
    brain_image_fu = sitk.ReadImage(brain_dicom_fu, sitk.sitkFloat32)
    # mask_image_bl = sitk.ReadImage(mask_dicom_bl, sitk.sitkFloat32)
    mask_image_fu = sitk.ReadImage(mask_dicom_fu, sitk.sitkFloat32)
    # print(f"{bone_image_bl.GetSpacing()=}")
    # print(f"{bone_image_bl.GetDirection()=}")
    # print(f"{bone_image_bl.GetOrigin()=}")
    # print(f"{bone_image_fu.GetSpacing()=}")
    # print(f"{bone_image_fu.GetDirection()=}")
    # print(f"{bone_image_fu.GetOrigin()=}")
    # print(f"{mask_image_fu.GetSpacing()=}")
    # print(f"{mask_image_fu.GetDirection()=}")
    # print(f"{mask_image_fu.GetOrigin()=}")
    transform_dcm = registration(brain_image_bl, brain_image_fu)
    # transform_mask = registration(mask_image_bl, mask_image_fu)
    registered_dcm = sitk.Resample(brain_image_fu, brain_image_bl, transform_dcm, sitk.sitkLinear, 0.0,
                                   brain_image_fu.GetPixelID())
    # registered_mask = sitk.Resample(mask_image_fu, mask_image_bl, transform_mask, sitk.sitkNearestNeighbor, 0.0,
    #                                 mask_image_fu.GetPixelID())

    registered_dcm.CopyInformation(brain_image_bl)
    # registered_mask.CopyInformation(mask_image_bl)
    # set_meta_data(bone_image_bl, registered_image, is_resample=True)
    registered_dcm = sitk.Cast(registered_dcm, sitk.sitkUInt16)
    os.makedirs(reg_path, exist_ok=True)
    # registered_mask = sitk.Cast(registered_mask, sitk.sitkUInt16)
    sitk.WriteImage(registered_dcm, os.path.join(reg_path, f"registered-ct-{date.today()}.dcm"))
    # sitk.WriteImage(registered_mask, os.path.join(reg_path, f"registered-mask-{date.today()}.dcm"))
    sitk.WriteTransform(transform_dcm, os.path.join(reg_path, f"registered-ct-tf-{date.today()}.tfm"))
    sitk.WriteTransform(transform_dcm, os.path.join(reg_path, f"registered-mask-tf-{date.today()}.tfm"))

    # print(f"mask_image: {mask_image.GetSize()}")
    # print(f"mask_image: {type(mask_image)}")
    # print(f"mask_image: {mask_image}")
    # print(f"bone_image_bl: {bone_image_bl.GetSize()}")
    # print(f"bone_image_bl: {bone_image_bl}")
    # print(f"bone_image_bl: {type(bone_image_bl)}")
    registration_mask(mask_image_fu, bone_image_bl, transform_dcm, reg_path)
