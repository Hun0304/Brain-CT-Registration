
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatasetsDir:
    """
        The class of datasets directories
    """
    ICH_PROJECT_DIR: Optional[str] = None
    REGISTRATION_DIR: Optional[str] = None
    DATASETS_DIR: Optional[str] = None

    def __str__(self):
        return f"REGISTRATION_DIR: {self.REGISTRATION_DIR}, DATASETS_DIR: {self.DATASETS_DIR}"

    def __repr__(self):
        return f"REGISTRATION_DIR: {self.REGISTRATION_DIR}, DATASETS_DIR: {self.DATASETS_DIR}"


@dataclass
class WindowSettings:
    """
    The window settings.
    """
    WL: int
    WW: int
    CT_MIN: int = None
    CT_MAX: int = None

    def __post_init__(self):
        if self.WL is None or self.WW is None:
            raise ValueError("Window Level and Window Width cannot be None.")
        if self.WW <= 0:
            raise ValueError("Window Width should be greater than 0.")

        self.CT_MIN = self.WL - self.WW // 2
        self.CT_MAX = self.WL + self.WW // 2

    def __str__(self):
        return f"Window Level: {self.WL}, Window Width: {self.WW}, CT_MAX: {self.CT_MAX}, CT_MIN: {self.CT_MIN}"

    def __repr__(self):
        return f"Window Level: {self.WL}, Window Width: {self.WW}, CT_MAX: {self.CT_MAX}, CT_MIN: {self.CT_MIN}"


# Datasets Directory
ICH_PROJECT_DIR = DatasetsDir(r"D:\MS\TRC-LAB\ICH Project")
ICH_127 = DatasetsDir(REGISTRATION_DIR=r"D:\MS\TRC-LAB\ICH Project\Registration\ICH_127",
                      DATASETS_DIR=r"D:\MS\TRC-LAB\ICH Datasets\ICH_127")
ICH_420 = DatasetsDir(REGISTRATION_DIR=r"D:\MS\TRC-LAB\ICH Project\Registration\ICH_420",
                      DATASETS_DIR=r"D:\MS\TRC-LAB\ICH Datasets\ICH_420")

# Window Settings
BRAIN_WINDOW = WindowSettings(40, 80)
BONE_WINDOW = WindowSettings(480, 2500)
SUBDURAL_WINDOW = WindowSettings(80, 200)
