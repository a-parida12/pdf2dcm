from .base import BaseConverter
from .utils import uid
from pathlib import Path
from typing import List
import os
from pydicom.dataset import FileMetaDataset, FileDataset


class Pdf2EncapsDCM(BaseConverter):
    def __init__(self):
        """Class for Encapsulated PDF generation"""
        super().__init__()

    def _get_encapspdf_meta(self) -> FileMetaDataset:
        """Get and set the file meta information for the pdf encaps dicom

        Returns:
            FileMetaDataset: header meta info of he dicom
        """
        # get generic meta information
        file_meta = self._get_dicom_meta()

        # set pdf encaps specific uids from the uid list
        file_meta.MediaStorageSOPClassUID = uid.ENCAPS_PDF_MEDIA_SOP_CLASS_UID
        file_meta.MediaStorageSOPInstanceUID = uid.ENCAPS_PDF_MEDIA_SOP_INSTANCE_UID
        file_meta.ImplementationClassUID = uid.ENCAPS_PDF_IMPL_CLASS_UID
        return file_meta

    def encapsulate_pdf(
        self, file_meta: FileMetaDataset, pdf_file_path: Path
    ) -> FileDataset:
        """method to encapsulate the pdf byte stream in a dicom

        Args:
            file_meta (FileMetaDataset): meta information of a dicom
            pdf_file_path (Path): path to the pdf file to be encapsulated

        Returns:
            FileDataset: encapsulated dicom pdf
        """
        ds = self._get_dicom_body(file_meta)
        ds.SOPClassUID = uid.ENCAPS_PDF_MEDIA_SOP_CLASS_UID

        # read the pdf byte stream put in the correct dicom loaction
        with open(pdf_file_path, "rb") as f:
            encaps_doc = f.read()
            ds.EncapsulatedDocument = (
                (encaps_doc + b"\0") if len(encaps_doc) % 2 != 0 else encaps_doc
            )

        # for encapsulation of pdf
        ds.MIMETypeOfEncapsulatedDocument = "application/pdf"
        ds.SpecificCharacterSet = "ISO_IR 100"

        return ds

    def run(
        self,
        path_pdf: str,
        path_template_dcm: str = "",
        suffix: str = ".dcm",
    ) -> List[Path]:
        """Run the complete encapsulation procedure on a given a pdf

        Args:
            path_pdf (str): path of the pdf that needs to be encapsulated
            path_template_dcm (str, optional): path to template for getting the
                                               repersonalisation of data.
            suffix (str, optional): suffix of the dicom files. Defaults to ".dcm".

        Returns:
            List[Path]: list path of the stored encapsulated dcm
        """
        # convert to path
        path_pdf_path = Path(path_pdf)
        path_template_dcm_path = Path(path_template_dcm)

        # encapsulate pdf
        encapspdf_meta = self._get_encapspdf_meta()
        encapspdf_dcm = self.encapsulate_pdf(encapspdf_meta, path_pdf_path)
        if path_template_dcm_path != Path("") and self.check_valid_dcm(
            path_template_dcm_path
        ):
            encapspdf_dcm = self.personalize_dcm(path_template_dcm_path, encapspdf_dcm)

        # save the pdfdicom
        name = path_pdf_path.stem
        path = path_pdf_path.parent
        save_path = Path(os.path.join(path, f"{name}{suffix}"))
        return [self._store_ds(save_path, encapspdf_dcm)]
