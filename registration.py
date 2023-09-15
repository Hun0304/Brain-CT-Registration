
import os
import SimpleITK as sitk

# from DICOM_2D_to_3D import set_meta_data


def registration(fixed_image, moving_image) -> sitk.Euler3DTransform:
    """
    # Registration
    :param fixed_image: baseline image
    :param moving_image: follow-up image
    :return: final_transform
    """
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation()
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)
    registration_method.SetInterpolator(sitk.sitkLinear)
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


def registration_mask(mask_3d, bl, tfm: sitk.Euler3DTransform) -> None:
    """
    # Using transform to 3d mask
    :param mask_3d: 3D mask
    :param bl: baseline image
    :param tfm: transform
    :return: None
    """
    # use transform to 3d mask
    # composed_transform = sitk.ComposeScaleSkewVersor3DTransform(tfm)
    # sitk.CompositeTransform(composed_transform)
    # print(type(tfm))
    registered_mask_3d = sitk.Resample(mask_3d, bl, sitk.sitkNearestNeighbor, 0.0, mask_3d.GetPixelID())
    registered_mask_3d = sitk.Cast(registered_mask_3d, sitk.sitkUInt16)
    print(f"{bl.GetSize()=}")
    print(f"{mask_3d.GetSize()=}")
    print(f"{registered_mask_3d.GetSize()=}")
    print(f"{registered_mask_3d.GetSpacing()=}")
    print(f"{registered_mask_3d.GetOrigin()=}")
    print(f"{registered_mask_3d.GetDirection()=}")
    sitk.WriteImage(registered_mask_3d, os.path.join(dir_path, "registered_mask_0914.dcm"))
    return None


if __name__ == '__main__':
    dir_path = r"C:\Users\Hun\Desktop\127 test\new_0825\registration"
    bone_dicom_path_BL = r"C:\Users\Hun\Desktop\127 test\new_0825\Case 1-1_brain_resample.dcm"
    bone_dicom_path_FU = r"C:\Users\Hun\Desktop\127 test\new_0825\Case 1-2_brain_resample.dcm"
    brain_dicom_path_BL = r"C:\Users\Hun\Desktop\127 test\new_0825\Case 1-1_brain_resample.dcm"
    mask_dicom_path_BL = r"C:\Users\Hun\Desktop\127 test\BL_Mask\Case 1-1-mask-resample.dcm"
    mask_dicom_path_FU = r"C:\Users\Hun\Desktop\127 test\FU_Mask\Case 1-2-mask-resample.dcm"
    bone_image_bl = sitk.ReadImage(bone_dicom_path_BL, sitk.sitkFloat32)
    bone_image_fu = sitk.ReadImage(bone_dicom_path_FU, sitk.sitkFloat32)
    brain_image_bl = sitk.ReadImage(brain_dicom_path_BL, sitk.sitkFloat32)
    mask_image_bl = sitk.ReadImage(mask_dicom_path_BL, sitk.sitkFloat32)
    mask_image_fu = sitk.ReadImage(mask_dicom_path_FU, sitk.sitkFloat32)
    # print(f"{bone_image_bl.GetSpacing()=}")
    # print(f"{bone_image_bl.GetDirection()=}")
    # print(f"{bone_image_bl.GetOrigin()=}")
    # print(f"{bone_image_fu.GetSpacing()=}")
    # print(f"{bone_image_fu.GetDirection()=}")
    # print(f"{bone_image_fu.GetOrigin()=}")
    # print(f"{mask_image_fu.GetSpacing()=}")
    # print(f"{mask_image_fu.GetDirection()=}")
    # print(f"{mask_image_fu.GetOrigin()=}")
    transform_dcm = registration(bone_image_bl, bone_image_fu)
    transform_mask = registration(mask_image_bl, mask_image_fu)
    registered_dcm = sitk.Resample(bone_image_fu, bone_image_bl, transform_dcm, sitk.sitkNearestNeighbor, 0.0,
                                   bone_image_fu.GetPixelID())
    registered_mask = sitk.Resample(mask_image_fu, mask_image_bl, transform_mask, sitk.sitkNearestNeighbor, 0.0,
                                    mask_image_fu.GetPixelID())

    registered_dcm.CopyInformation(bone_image_bl)
    registered_mask.CopyInformation(mask_image_bl)
    # set_meta_data(bone_image_bl, registered_image, is_resample=True)
    registered_dcm = sitk.Cast(registered_dcm, sitk.sitkUInt16)
    registered_mask = sitk.Cast(registered_mask, sitk.sitkUInt16)
    sitk.WriteImage(registered_dcm, os.path.join(dir_path, "registered_ct_0914.dcm"))
    sitk.WriteImage(registered_mask, os.path.join(dir_path, "registered_mask_0914.dcm"))
    sitk.WriteTransform(transform_dcm, os.path.join(dir_path, "registered_tf_0914.tfm"))
    sitk.WriteTransform(transform_dcm, os.path.join(dir_path, "registered_mask_tf_0914.tfm"))

    # print(f"mask_image: {mask_image.GetSize()}")
    # print(f"mask_image: {type(mask_image)}")
    # print(f"mask_image: {mask_image}")
    # print(f"bone_image_bl: {bone_image_bl.GetSize()}")
    # print(f"bone_image_bl: {bone_image_bl}")
    # print(f"bone_image_bl: {type(bone_image_bl)}")
    # registration_mask(mask_image_fu, bone_image_bl, transform_dcm)
