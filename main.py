"""
Main file.
"""

from tqdm.rich import tqdm

from common.globel_veriable import ICH_420_DIR
from mysys.io.input import HematomaExpansionDataInputProcessor
from collections import Counter


def main():
    """
    Main function.
    """
    he_data = HematomaExpansionDataInputProcessor(ICH_420_DIR.REGISTRATION_DIR, "ICH_420").he_data_reader()
    for row in he_data:
        print(row)

    return None


if __name__ == '__main__':
    main()
