
import os
from typing import List

import cv2
import numpy as np

from tqdm import tqdm


def find_max_area(ct_image: np.ndarray) -> np.ndarray:
    """
    Find the max area of the contour.
    :param ct_image: The CT image.
    :return: The max area of the contour.
    """
    max_mask = []
    for i in range(ct_image.shape[0]):
        contours, _ = cv2.findContours(ct_image[i], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours) == 0:
            continue
        max_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros(ct_image[i].shape, np.uint8)
        cv2.drawContours(mask, [max_contour], 0, 255, thickness=cv2.FILLED)
        max_mask.append(mask)
    return np.array(max_mask)


def denoise(brain: np.ndarray, bone: np.ndarray) -> np.ndarray:
    """
    Denoise the image.
    :param brain: brain image.
    :param bone: bone image.
    :return: Denoised image.
    """
    denoised_image = np.zeros(bone.shape, dtype=np.uint8)
    white_pixels = (bone == 255)
    denoised_image[white_pixels] = brain[white_pixels]

    return denoised_image


def merge_image(masks: List, mask_dir: str) -> None:
    """
    Merge the masks with the same name.
    :param masks: The list of masks.
    :param mask_dir: The directory of masks.
    :return: None
    """
    temp = masks[0]
    for mask in masks[1:]:
        name = mask[:mask.rfind("-")]
        if temp[:temp.rfind("-")] == name:
            image_1 = cv2.imread(os.path.join(mask_dir, mask))
            image_2 = cv2.imread(os.path.join(mask_dir, temp))
            merge = cv2.add(image_1, image_2)
            cv2.imwrite(os.path.join(mask_dir, name + ".tif"), merge)
            os.remove(os.path.join(mask_dir, mask))
            os.remove(os.path.join(mask_dir, temp))
        else:
            temp = mask
    return None
