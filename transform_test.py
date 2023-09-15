
import SimpleITK as sitk

# 讀取保存的變換
alignment_transform = sitk.ReadTransform(r"C:\Users\Hun\Desktop\127 test\new_0825\registration\registered_tf_0914.tfm")

# 輸出變換的參數
print(f"變換參數:\n{alignment_transform}")

# 讀取要驗證的DICOM影像
image_to_verify = sitk.ReadImage('要驗證的影像.dcm')

# 將變換應用於影像
transformed_image = sitk.Resample(image_to_verify, alignment_transform)

# 嘗試應用逆變換
inverse_transform = alignment_transform.GetInverse()
restored_image = sitk.Resample(transformed_image, inverse_transform)

# 比較原始影像和恢復的影像
diff_image = image_to_verify - restored_image
print(f"最大像素差異: {sitk.GetArrayViewFromImage(diff_image).max()}")
