from .base import BaseConverter
from .utils import uid
from pathlib import Path
import os


from pydicom.dataset import Dataset, FileDataset


class Pdf2EncapsPdf(BaseConverter):
    def __init__(self):
        pass

    def _get_encapspdf_meta(self) -> FileDataset:
        file_meta = self._get_dicom_meta()
        file_meta.MediaStorageSOPClassUID = uid.ENCAPS_PDF_MEDIA_SOP_CLASS_UID
        file_meta.MediaStorageSOPInstanceUID = uid.ENCAPS_PDF_MEDIA_SOP_INSTANCE_UID
        file_meta.ImplementationClassUID = uid.ENCAPS_PDF_IMPL_CLASS_UID
        return file_meta

    def encapsulate_pdf(self, file_meta, pdf_file_path) -> Dataset:
        ds = self._get_dicom_body(file_meta)
        ds.SOPClassUID = uid.ENCAPS_PDF_MEDIA_SOP_CLASS_UID

        with open(pdf_file_path, "rb") as f:
            ds.EncapsulatedDocument = f.read()

        # for encapsulation of pdf
        ds.MIMETypeOfEncapsulatedDocument = "application/pdf"
        ds.SpecificCharacterSet = "ISO_IR 100"

        return ds

    def run(
        self,
        path_pdf: Path,
        path_template_dcm: Path = Path(""),
        suffix: str = ".dcm",
    ) -> Path:

        encapspdf_meta = self._get_encapspdf_meta()
        encapspdf_dcm = self.encapsulate_pdf(encapspdf_meta, path_pdf)
        if path_template_dcm != "" and self.check_valid_dcm(path_template_dcm):
            encapspdf_dcm = self.personalize_dcm(path_template_dcm, encapspdf_dcm)

        name = Path(path_pdf).stem
        path = Path(path_pdf).parent

        save_path = Path(os.path.join(path, f"{name}{suffix}"))
        return self._store_ds(save_path, encapspdf_dcm)
