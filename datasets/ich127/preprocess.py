
import os

from tqdm import tqdm
from shutil import copy2
from natsort import natsorted

from common.globel_veriable import REGISTRATION_DIR_127, REGISTRATION_DIR_420
from common.utils import create_dir
from mask_Resample import mask2Dto3D


def preprocess_127_dir(dir: str) -> None:
    """
    Preprocess the directory.
    :param dir: The directory of the images.
    :return: None
    """
    error_list = []
    datasets_list = natsorted(os.listdir(dir))
    case_name = datasets_list[0][:datasets_list[0].find("-")]
    for idx, f in enumerate(datasets_list, start=1):
        if case_name == f[:f.find("-")]:
            # print(f"{case_name}", f"{f=}", f"{idx=}")
            if idx == len(datasets_list):
                break
            case_name = datasets_list[idx][:datasets_list[idx].find("-")]
            print(os.path.join(REGISTRATION_DIR_127, case_name))
            dicom_bl, dicom_fu, mask_bl, mask_fu = create_dir(os.path.join(REGISTRATION_DIR_127, case_name))
            print(os.path.join(dir, datasets_list[idx]))
            # copy2(os.path.join(dir, datasets_list[idx]), os.path.join(mask_fu, datasets_list[idx]))
            os.makedirs(os.path.abspath(os.path.join(mask_fu, "../..", "result")), exist_ok=True)
            print(len(os.listdir(os.path.abspath(os.path.join(mask_fu, "../..", "result")))))
            if datasets_list[idx] == datasets_list[idx + 1]:
                continue
            try:
                mask2Dto3D(mask_fu, dicom_fu)
            except:
                pass

    return None
