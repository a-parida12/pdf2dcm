from pathlib import Path
import pydicom
from pydicom.dataset import FileMetaDataset, FileDataset
from pydicom.errors import InvalidDicomError
from abc import ABC, abstractmethod

from .utils.uid import generate_random_uid
import tempfile
from typing import List
import datetime

import warnings


class BaseConverter(ABC):
    def __init__(self):
        self.repersonalisation_fields = [
            "PatientName",
            "PatientID",
            "PatientSex",
            "StudyInstanceUID",
            "SeriesInstanceUID",
            "SOPInstanceUID",
        ]

    def personalize_dcm(
        self, template_dcm_path: Path, pdf_dcm: FileDataset
    ) -> FileDataset:
        template_dcm = pydicom.dcmread(template_dcm_path)

        for field in self.repersonalisation_fields:
            try:
                pdf_dcm[field] = template_dcm[field]
            except KeyError:
                if "UID" in field:
                    pdf_dcm.add_new(field, "UI", generate_random_uid())
                    warning_msg = f"""{field} not found in DICOM {template_dcm_path},
                    using randomly generated values!"""
                else:
                    # need to get the corresponding VR for the field
                    pdf_dcm.add_new(field, "PN", "")
                    warning_msg = f"""{field} not found in DICOM {template_dcm_path},
                    leaving the field empty!"""

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
        file_meta.TransferSyntaxUID = (
            "1.2.840.10008.1.2.1"  # std transfer uid little endian, implicit vr
        )
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

        ds.is_little_endian = True
        ds.is_implicit_VR = False

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
        ds.fix_meta_info()
        ds.save_as(store_path)
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
