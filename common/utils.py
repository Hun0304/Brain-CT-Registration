
import os
import json
import matplotlib.pyplot as plt

from typing import Tuple


def visualization_hist(json_file: json) -> None:
    """
    Visualize the histogram.
    :param json_file: The json file.
    :return: None
    """
    values = []
    with open(json_file, "r+") as f:
        file = json.load(f)
        for value in file.values():
            values.append(abs(value))
        plt.hist(values, bins=20, color="steelblue", edgecolor="k", alpha=0.65, rwidth=0.8)
        plt.xlabel("Registration metric value")
        plt.ylabel("Frequency")
        plt.title(f"Registration metric value histogram, total={len(values)}")
        plt.savefig(os.path.abspath(os.path.join(json_file, "../..", "histogram.png")))
        # plt.show()

    return None


def create_dir(dir) -> Tuple[str, str, str, str]:
    """
    Create directory.
    :param dir: The directory of the images.
    :return: The directory of the images.
    """
    dicom_bl_dir = os.path.join(dir, "dcm", "BL")
    dicom_fu_dir = os.path.join(dir, "dcm", "FU")
    mask_bl_dir = os.path.join(dir, "mask", "BL")
    mask_fu_dir = os.path.join(dir, "mask", "FU")

    os.makedirs(dicom_bl_dir, exist_ok=True)
    os.makedirs(dicom_fu_dir, exist_ok=True)
    os.makedirs(mask_bl_dir, exist_ok=True)
    os.makedirs(mask_fu_dir, exist_ok=True)

    return dicom_bl_dir, dicom_fu_dir, mask_bl_dir, mask_fu_dir
