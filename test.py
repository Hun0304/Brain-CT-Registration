import glob
import os
import pandas as pd
import numpy as np

nii_dir = r"D:\MS\TRC-LAB\ICH Datasets\PhysioNet_ICH"
nii_label = os.path.join(nii_dir, "hemorrhage_diagnosis_raw_ct.csv")
nii_images = glob.glob(os.path.join(nii_dir, "ct_scans", "*.nii"))

ICHType = {"NOT_ANY": 0, "INTRAPARENCHYMAL": 1, "INTRAVENTRICULAR": 2, "SUBARACHNOID": 4, "SUBDURAL": 8, "EPIDURAL": 16}
diagnosis_label = ICHType["NOT_ANY"]

train_labels = pd.read_csv(nii_label)
diagnosis_columns = ["PatientNumber", "Intraparenchymal", "Intraventricular", "Subarachnoid", "Subdural", "Epidural"]
diagnosis_labels = train_labels.loc[:, diagnosis_columns]
# print(diagnosis_labels)
# print(train_labels["PatientNumber"])
# print(diagnosis_labels["PatientNumber"])
for idx in diagnosis_labels["PatientNumber"]:
    patient_labels = diagnosis_labels.loc[diagnosis_labels["PatientNumber"] == idx]
    patient_labels.index = pd.RangeIndex(start=1, stop=len(patient_labels) + 1, step=1)
    for labels in patient_labels.iterrows():
        for i, label in enumerate(labels[1][1:], start=1):
            if label == 1:
                # print(labels)
                diagnosis_label |= ICHType[diagnosis_columns[i].upper()]
        print(labels, diagnosis_label)
        diagnosis_label = ICHType["NOT_ANY"]
        # print(labels[1][1:])


    # for labels in patient_labels.loc[diagnosis_labels["PatientNumber"] == idx, diagnosis_columns[1:]].values:
    #     # print(labels)
    #     if labels.sum() > 0:
    #         for i in range(1, len(labels)):
    #             if labels[i] == 1:
    #                 diagnosis_label |= ICHType[diagnosis_labels.columns[i].upper()]
    #             print(diagnosis_label)
    #     diagnosis_label = ICHType["NOT_ANY"]

    # for i, row in patient_labels.iterrows():
    #     if row[1:].sum() > 0:
    #         diagnosis_label |= diagnosis_columns[i].upper()


    # print(idx, patient_labels.loc[diagnosis_labels["PatientNumber"] == idx, diagnosis_columns[1:]].values)
    break



