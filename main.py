import os
import glob2
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from tqdm import tqdm


np.set_printoptions(precision=2, suppress=True)

PHYSIONET_DATASET = r"D:\MS\TRC-LAB\ICH Datasets\PhysioNet_ICH"
DATASET_NII = os.path.join(PHYSIONET_DATASET, "ct_scans")
DATASET_LABEL = os.path.join(PHYSIONET_DATASET, "masks")

# CT_min, CT_max = image.min(), image.max()
CT_min, CT_max = 0, 80
window_level = (CT_max + CT_min) / 2
window_width = CT_max - CT_min


def adjust_image_window(_image, _slope, _intercept, bit=12, dtype=np.uint16):
    max_val = 2 ** bit
    _A = max_val / window_width * _slope
    _B = (max_val / 2) - (max_val * window_level / window_width) + _A * _intercept
    adjusted_image = _A * _image + _B
    adjusted_image = np.clip(adjusted_image, 0, max_val - 1)

    return adjusted_image.astype(dtype=dtype)


def get_adjust_slices_data(nii_data, key, flag=1):
    nii_dataobj = nii_data.dataobj
    slope = nii_dataobj.slope
    intercept = nii_dataobj.inter

    result = nii_dataobj.get_unscaled()
    if key == "images" and flag == 1:
        result = adjust_image_window(
            result, slope, intercept
        )

    return {
        "slope": slope,
        "intercept": intercept,
        "data": result
    }


def extract_slices(paired_nii):
    paired_nii["data"] = {}
    for key, filepath in paired_nii["metadata"]["filepath"].items():
        nii_data = nib.load(filepath)
        slices_data = get_adjust_slices_data(nii_data, key)
        paired_nii["data"][key] = slices_data

    return paired_nii


def get_paired_nii_filepath(nii_image_filepath):
    image_fn = os.path.basename(nii_image_filepath)
    label_fn = image_fn
    return {
      "metadata": {
          "filepath": {
            "images": nii_image_filepath,
            "masks": os.path.join(DATASET_LABEL, label_fn)
          }
      }
    }

paired_nii_list = [get_paired_nii_filepath(image_fp) for image_fp in tqdm(glob2.glob(os.path.join(DATASET_NII, "*.nii")), desc="Pair Images")]
origin_data = data = paired_nii_list[0]
data = extract_slices(data)


origin_data_slices = [get_adjust_slices_data(nib.load(filepath), key, 0) for key, filepath in origin_data["metadata"]["filepath"].items()]
paired_slices = [extract_slices(paired_nii) for paired_nii in tqdm(paired_nii_list[0:1], desc="Extract")]

images = paired_slices[0]["data"]["images"]["data"].T
masks = paired_slices[0]["data"]["masks"]["data"].T
origin_images = origin_data_slices[0]["data"].T

mask_data_rgb = np.zeros((masks.shape[0], masks.shape[1], masks.shape[2], 3), dtype=np.uint8)
mask_data_rgb[masks > 0] = [0, 0, 255]  # 藍色為 [0, 0, 255]

print(origin_images.shape)
print(images.shape)
print(masks.shape)

for origin_image, image, mask, mask_rgb, slice_number in zip(origin_images, images, masks, mask_data_rgb, range(1, origin_images.shape[0]+1)):
    fig = plt.figure(figsize=(10, 10))
    fig.suptitle(f"Slice: {str(slice_number)}", fontsize=16)

    plt.subplot(2, 2, 1)
    plt.title("Origin Image")
    plt.imshow(origin_image, cmap=plt.cm.gray, origin="lower")
    plt.axis("off")

    plt.subplot(2, 2, 2)
    plt.title("Windowing (80, 40)")
    plt.imshow(image, cmap=plt.cm.gray, origin="lower")
    plt.axis("off")

    plt.subplot(2, 2, 3)
    plt.title("Mask")
    plt.imshow(mask, cmap=plt.cm.gray, origin="lower")
    plt.axis("off")

    plt.subplot(2, 2, 4)
    plt.title("Fusion")
    mask_rgb = np.where(mask_rgb == [0, 0, 255], [0, 0, 255], [0, 0, 0])
    # 將遮罩影像轉換為藍色
    plt.imshow(image, cmap=plt.cm.gray, origin="lower")
    plt.imshow(mask_rgb, origin="lower", alpha=0.1)
    plt.imshow(mask_rgb, origin="lower", alpha=0.1)
    plt.imshow(mask_rgb, origin="lower", alpha=0.1)
    plt.imshow(mask_rgb, origin="lower", alpha=0.1)
    plt.imshow(mask_rgb, origin="lower", alpha=0.1)

    plt.tight_layout()
    plt.axis("off")
    plt.show()
