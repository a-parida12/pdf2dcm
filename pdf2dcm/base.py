from pathlib import Path
import pydicom
from pydicom.datadict import dictionary_VR, tag_for_keyword
from pydicom.dataelem import empty_value_for_VR
from pydicom.dataset import FileMetaDataset, FileDataset, validate_file_meta
from pydicom.errors import InvalidDicomError
from abc import ABC, abstractmethod

from pydicom.uid import generate_uid, ExplicitVRLittleEndian

import tempfile
from typing import List
import datetime

import warnings


class BaseConverter(ABC):
    def __init__(self, repersonalisation_fields=[]):
        if len(repersonalisation_fields):
            self.repersonalisation_fields = repersonalisation_fields
        else:
            self.repersonalisation_fields = [
                "PatientName",
                "PatientID",
                "PatientSex",
                "StudyInstanceUID",
            ]

    def personalize_dcm(
        self, template_dcm_path: Path, pdf_dcm: FileDataset
    ) -> FileDataset:
        template_dcm = pydicom.dcmread(template_dcm_path)

        for field in self.repersonalisation_fields:
            tag = tag_for_keyword(field)
            if tag is None:
                raise ValueError(f"Unknown DICOM keyword: {field}")

            vr = dictionary_VR(tag)
            try:
                pdf_dcm[tag] = template_dcm[tag]
            except KeyError:
                if vr == "UI":
                    value = generate_uid()
                    warning_msg = f"""{field} not found in DICOM {template_dcm_path},
                    using randomly generated values!"""
                else:
                    value = empty_value_for_VR(vr)
                    warning_msg = f"""{field} not found in DICOM {template_dcm_path},
                    leaving the field empty!"""

                pdf_dcm.add_new(tag, vr, value)
                warnings.warn(warning_msg)

        return pdf_dcm

    @staticmethod
    def _get_dicom_meta() -> FileMetaDataset:
        """Generates the file meta-data for a DICOM PDF

        Returns:
            FileMetaDataset: dcm header with meta information
        """

        file_meta = FileMetaDataset()
        file_meta.FileMetaInformationVersion = b"\x00\x01"
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        file_meta.ImplementationVersionName = "pdf2dcm"
        return file_meta

    @staticmethod
    def _get_dicom_body(meta: FileMetaDataset) -> FileDataset:
        """Creates a temporary file as part of the DICOM PDF creation process

        Args:
            meta (FileMetaDataset): the meta information of the dicom file

        Returns:
            FileDataset: dicom file body information
        """
        filename = tempfile.NamedTemporaryFile().name
        ds = FileDataset(filename, {}, file_meta=meta, preamble=b"\0" * 128)

        ds.SOPInstanceUID = generate_uid()

        # if we want to create the pdf with the pdf creation timing
        dt = datetime.datetime.now()
        ds.ContentDate = dt.strftime("%Y%m%d")
        timeStr = dt.strftime("%H%M%S.%f")
        ds.ContentTime = timeStr

        ds.Modality = "DOC"  # document
        ds.ConversionType = "WSD"  # workstation
        return ds

    @staticmethod
    def _store_ds(store_path: Path, ds: FileDataset) -> Path:
        """check and store the dicom at a given location

        Args:
            store_path (Path): output storage path for the pdf dicom
            ds (FileDataset): the dicom pdf

        Returns:
            [Path]: output storage path for the pdf dicom
        """
        validate_file_meta(ds.file_meta)
        ds.save_as(store_path, enforce_file_format=True)
        return store_path

    @staticmethod
    def check_valid_dcm(path: Path) -> bool:
        """check whether given file is a dicom or not

        Args:
            path (Path): path to a dicom file

        Returns:
            bool: boolean value True for dicom else False
        """
        try:
            pydicom.dcmread(path, defer_size=1024)
        except InvalidDicomError:
            return False

        return True

    @abstractmethod
    def run(self, path_pdf: str, path_template_dcm: str, suffix: str) -> List[Path]:
        pass
