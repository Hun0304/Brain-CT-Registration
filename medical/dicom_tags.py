"""
    File: dicom_tags.py
    Description: This file contains the metadata tags for the DICOM files.
"""

from dataclasses import dataclass


@dataclass
class MetaDataTags:
    """
    The class of metadata tags.
    """
    STUDY_DATE: str = "0008|0020"
    STUDY_TIME: str = "0008|0030"
    MODALITY: str = "0008|0060"
    MANUFACTURER: str = "0008|0070"
    PATIENT_NAME: str = "0010|0010"
    PATIENT_ID: str = "0010|0020"
    SLICE_THICKNESS: str = "0018|0050"
    IMAGE_ORIGIN: str = "0020|0032"
    IMAGE_ORIENTATION: str = "0020|0037"
    PIXEL_SPACING: str = "0028|0030"
    WINDOW_CENTER: str = "0028|1050"
    WINDOW_WIDTH: str = "0028|1051"
    INTERCEPT: str = "0028|1052"
    SLOPE: str = "0028|1053"
