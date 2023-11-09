
import os
import re

from tqdm import tqdm
from shutil import copy2
from natsort import natsorted

from common.globel_veriable import REGISTRATION_DIR_420


def preprocess_420_dir(dir: str) -> None:
    """
    Preprocess the directory.
    :param dir:
    """
    datasets_list = natsorted(os.listdir(dir))
    patten = r'Case_\d+-\d+|Spon_Case_\d+-\d+'
    for d in tqdm(datasets_list):
        case_name = re.search(patten, d).group(0).split("-")[0].replace("_", " ")
        bl_fu = re.search(patten, d).group(0).split("-")[1]
        if bl_fu == "1":
            bl_fu = "BL"
        elif bl_fu == "2":
            bl_fu = "FU"
        # print(os.path.join(REGISTRATION_DIR_420, case_name, "dcm", bl_fu))
        # os.makedirs(os.path.join(REGISTRATION_DIR_420, case_name, "mask", bl_fu), exist_ok=True)
        if re.search(patten, d).group(0)[-2:] == "-1":
            copy2(os.path.join(dir, d), os.path.join(REGISTRATION_DIR_420, case_name, "mask", "BL"))
        elif re.search(patten, d).group(0)[-2:] == "-2":
            copy2(os.path.join(dir, d), os.path.join(REGISTRATION_DIR_420, case_name, "mask", "FU"))

    return None
