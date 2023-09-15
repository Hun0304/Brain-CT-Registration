
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt

# window settings
# CT_min, CT_max = 0, 80     # brain WW: 80, WL: 40
# CT_min, CT_max = -20, 180  # subdural WW: 200, WL: 80
CT_min, CT_max = -800, 2000  # temporal bone WW: 2800, WL: 600

window_width = CT_max - CT_min
window_level = (CT_max + CT_min) // 2


def adjust_image(image_bl, image_fu, ct_min, ct_max, ww):
    adjusted_image_bl = np.clip(image_bl, ct_min, ct_max).astype(np.float32)
    adjusted_image_fu = np.clip(image_fu, ct_min, ct_max).astype(np.float32)
    adjusted_image_bl = (adjusted_image_bl - ct_min) / ww * 255
    adjusted_image_fu = (adjusted_image_fu - ct_min) / ww * 255
    adjusted_image_bl = adjusted_image_bl.astype(np.uint8)
    adjusted_image_fu = adjusted_image_fu.astype(np.uint8)

    return adjusted_image_bl, adjusted_image_fu


def command_iteration(filter):
    print(f"{filter.GetElapsedIterations():3} = {filter.GetMetric():10.5f}")


def demons_registration() -> None:
    demons_filter = sitk.DemonsRegistrationFilter()
    demons_filter.SetNumberOfIterations(50)
    demons_filter.SetStandardDeviations(1.0)
    demons_filter.AddCommand(sitk.sitkIterationEvent, lambda: command_iteration(demons_filter))
    displacement_field = demons_filter.Execute(adjusted_image_sitk_FU, adjusted_image_sitk_BL)
    sitk.WriteImage(displacement_field, "demons.mha")


if __name__ == '__main__':
    raw_image_path_BL = r"C:\Users\Hun\Desktop\127 test\Case 1-1_test.dcm"
    raw_image_path_FU = r"C:\Users\Hun\Desktop\127 test\Case 1-2_test.dcm"
    image_reader = sitk.ImageFileReader()
    image_reader.SetImageIO("GDCMImageIO")
    image_reader.SetFileName(raw_image_path_BL)
    image_reader.ReadImageInformation()
    # print(image_reader.GetMetaDataKeys())

    # Patient's Name Tag
    # tag = '0010|0010'

    # Rescale Intercept Tag
    # inter_tag = '0028|1052'
    # Rescale Slope Tag
    # slope_tag = '0028|1053'

    # inter = image_reader.GetMetaData(inter_tag)
    # slope = image_reader.GetMetaData(slope_tag)

    raw_image_sitk_BL = sitk.ReadImage(raw_image_path_BL, sitk.sitkFloat32)
    raw_image_sitk_FU = sitk.ReadImage(raw_image_path_FU, sitk.sitkFloat32)
    raw_image_BL = sitk.GetArrayFromImage(raw_image_sitk_BL)
    raw_image_FU = sitk.GetArrayFromImage(raw_image_sitk_FU)

    # adjusted_image_BL, adjusted_image_FU = adjust_image(image_bl=raw_image_BL,
    #                                                     image_fu=raw_image_FU,
    #                                                     ct_min=CT_min,
    #                                                     ct_max=CT_max,
    #                                                     ww=window_width)
    # plt.axis('off')
    # plt.imshow(adjusted_image_BL[0], cmap='gray')
    # plt.show()
    # plt.axis('off')
    # plt.imshow(adjusted_image_FU[0], cmap='gray')
    # plt.show()

    # save image
    # sitk.WriteImage(sitk.GetImageFromArray(raw_image_BL), "image_BL.mha")
    # sitk.WriteImage(sitk.GetImageFromArray(raw_image_FU), "image_FU.mha")
    #
    # adjusted_image_sitk_BL = sitk.ReadImage("adjusted_image_BL.mha", sitk.sitkFloat32)
    # adjusted_image_sitk_FU = sitk.ReadImage("adjusted_image_FU.mha", sitk.sitkFloat32)

    # Demons registration
    # demons_registration()

    # MetricAsMeanSquares registration
    # registration_method = sitk.ImageRegistrationMethod()
    # registration_method.SetMetricAsMeanSquares()
    # registration_method.SetOptimizerAsRegularStepGradientDescent(learningRate=1.0,
    #                                                              minStep=0.001,
    #                                                              numberOfIterations=100)
    # final_transform = registration_method.Execute(adjusted_image_sitk_FU,
    #                                               adjusted_image_sitk_BL)
    # registered_image = sitk.Resample(adjusted_image_sitk_FU,
    #                                  adjusted_image_sitk_BL,
    #                                  final_transform,
    #                                  sitk.sitkLinear,
    #                                  0.0,
    #                                  adjusted_image_sitk_FU.GetPixelID())

    # sitk.WriteImage(registered_image, "registered_ct_slice.mha")
    initial_transform = sitk.CenteredTransformInitializer(raw_image_sitk_BL,
                                                          raw_image_sitk_FU,
                                                          sitk.Euler3DTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)
    registration_method = sitk.ImageRegistrationMethod()

    # Similarity metric settings.
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)
    registration_method.SetInterpolator(sitk.sitkLinear)

    # Optimizer settings.
    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0,
                                                      numberOfIterations=1000,
                                                      convergenceMinimumValue=1e-6,
                                                      convergenceWindowSize=10)

    registration_method.SetOptimizerScalesFromPhysicalShift()

    # Setup for the multi-resolution framework.
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors=[4, 2, 1])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[2, 1, 0])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    # Don't optimize in-place, we would possibly like to run this cell multiple times.
    registration_method.SetInitialTransform(initial_transform, inPlace=False)

    # Connect all of the observers so that we can perform plotting during registration.
    # registration_method.AddCommand(sitk.sitkStartEvent, start_plot)
    # registration_method.AddCommand(sitk.sitkEndEvent, end_plot)
    # registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, update_multires_iterations)

    registration_method.AddCommand(sitk.sitkIterationEvent, lambda: command_iteration(registration_method))

    final_transform = registration_method.Execute(raw_image_sitk_BL, raw_image_sitk_FU)

    print(f'Final metric value: {registration_method.GetMetricValue()}')
    print(f'Optimizer\'s stopping condition, {registration_method.GetOptimizerStopConditionDescription()}')






    # Registration_image = sitk.ReadImage("demons.mha", sitk.sitkFloat32)
    # Registration_image_1 = sitk.GetArrayFromImage(Registration_image)
    # print(Registration_image_1)
    # plt.axis('off')
    # plt.imshow(Registration_image_1[0], cmap='gray')
    # plt.show()
