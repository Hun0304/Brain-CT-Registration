"""
 分割資料集包含 HE or NOT HE
"""

import os
import pandas as pd

from tqdm import tqdm
from natsort import natsorted

from common.globel_veriable import ICH_PROJECT_DIR


def get_excel_data():
    """
    Get the data from excel.
    :return: The data of excel.
    """
    excel_path = os.path.join(ICH_PROJECT_DIR, "0-4 HR ICH all patient list.xlsx")
    df = pd.read_excel(excel_path, sheet_name="0-4 HR")
    HEs = df["HE"].tolist()
    case_numbers = df["Case number"].tolist()
    for he, case in zip(HEs, case_numbers):
        if he == 1:
            print(case)
    # print(HEs)
    # print(case_numbers)
    return 0

