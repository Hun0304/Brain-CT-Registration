import SimpleITK as sitk
import numpy as np


def resample_image(new_image, new_shape, new_spacing):
    original_shape = new_image.GetSize()
    original_spacing = new_image.GetSpacing()

    scaling_factors = np.divide(original_spacing, new_spacing)

    resampled_image = sitk.Resample(new_image,
                                    new_shape,
                                    sitk.Transform(),
                                    sitk.sitkLinear,
                                    new_image.GetOrigin(),
                                    new_spacing,
                                    new_image.GetDirection(),
                                    0.0,
                                    new_image.GetPixelIDValue())
    return resampled_image


def apply_windowing(image, window_center, window_width):
    """
    # Apply windowing to an image.
    :param image:
    :param window_center:
    :param window_width:
    :return:
    """
    min_intensity = window_center - window_width // 2.0
    max_intensity = window_center + window_width // 2.0
    windowed_image = sitk.IntensityWindowing(image, min_intensity, max_intensity, 0.0, 255.0)
    return windowed_image


# 讀取DICOM影像
reader = sitk.ImageSeriesReader()
series_IDs = reader.GetGDCMSeriesIDs(r"C:\Users\Hun\Desktop\127 test\BL")
if len(series_IDs) == 0:
    print("No DICOM series found in the provided folder.")
    exit()
series_file_names = reader.GetGDCMSeriesFileNames(r"C:\Users\Hun\Desktop\127 test\BL", series_IDs[0])
reader.SetFileNames(series_file_names)
image = reader.Execute()

# 對每一個切片進行窗口設定
windowed_slices = []
for z in range(image.GetSize()[0]):
    slice_image = image[z, :, :]
    windowed_slice = apply_windowing(slice_image, window_center=0, window_width=80)
    windowed_slices.append(windowed_slice)

# 將窗口設定後的切片重新組合成影像
windowed_image = sitk.JoinSeries(windowed_slices)

# 重新採樣影像
new_size = (256, 256, 180)
new_spacing = (1.0, 1.0, 1.0)
resampled_image = resample_image(windowed_image, new_size, new_spacing)

# 檢視結果
print("原始影像大小:", image.GetSize())
print("原始影像間距:", image.GetSpacing())
print("窗口設定後影像大小:", windowed_image.GetSize())
print("窗口設定後影像間距:", windowed_image.GetSpacing())
print("重新採樣後影像大小:", resampled_image.GetSize())
print("重新採樣後影像間距:", resampled_image.GetSpacing())

output_path = r'C:\Users\Hun\Desktop\127 test\Case 1-1_.dcm'
sitk.WriteImage(resampled_image, output_path)
