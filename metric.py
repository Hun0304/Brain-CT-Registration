
import numpy as np
import SimpleITK as sitk


def hausdorff_distance(bl: sitk.Image, fu: sitk.Image, params: np.array):
    """
    # Calculate the Hausdorff distance.
    :param bl: baseline image
    :param fu: follow-up image
    :param params: initial params
    :return: Hausdorff distance
    """
    # initial params 平移和旋轉的參數
    translation_x, translation_y, translation_z, rotation_x, rotation_y, rotation_z = params

    # 定義平移轉換
    translation = sitk.TranslationTransform(3, [translation_x, translation_y, translation_z])

    # 定義旋轉轉換
    rotation = sitk.Euler3DTransform()
    rotation.SetRotation(*np.radians([rotation_x, rotation_y, rotation_z]))

    # 組合平移和旋轉轉換
    composite_transform = sitk.CompositeTransform([translation, rotation])

    # 將轉換應用於其中一張影像
    transformed_image1 = sitk.Resample(fu, composite_transform)

    # 計算3D Hausdorff距離
    hausdorff_filter = sitk.HausdorffDistanceImageFilter()
    hausdorff_filter.Execute(transformed_image1, bl)
    current_hausdorff_distance = hausdorff_filter.GetHausdorffDistance()
    # print(f"{composite_transform.GetParameters()}")
    return composite_transform.GetParameters()


def metric_main(bl: sitk.Image, fu: sitk.Image) -> None:
    """
    # Main function.
    :param bl: baseline image
    :param fu: follow-up image
    :return:
    """
    # 初始參數值，可以根據需求設定
    initial_params = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    learning_rate = 0.1  # 學習率
    num_iterations = 100  # 迭代次數
    for i in range(num_iterations):
        # 計算目標函數的梯度
        gradient = np.gradient(hausdorff_distance(bl, fu, initial_params), initial_params)

        # 更新參數值
        initial_params -= learning_rate * gradient

        # 顯示目前的Hausdorff距離和參數值
        current_hausdorff_distance = hausdorff_distance(bl, fu, initial_params)
        print(f"Iteration {i + 1}, Hausdorff Distance: {current_hausdorff_distance}, Parameters: {initial_params}")

    # 最後的 initial_params 即為最佳的平移和旋轉參數
    print("最佳參數:", initial_params)
    