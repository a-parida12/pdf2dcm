import pytest
import os

from pdf2dcm.utils import uid
import pydicom
from pydicom.dataset import FileMetaDataset, FileDataset


@pytest.mark.pdfencaps
def test_02_1_get_encapspdf_meta(pdfencapsconverter):
    file_meta = pdfencapsconverter._get_encapspdf_meta()

    assert type(file_meta) == FileMetaDataset
    assert file_meta.MediaStorageSOPClassUID == uid.ENCAPS_PDF_MEDIA_SOP_CLASS_UID
    assert file_meta.MediaStorageSOPInstanceUID == uid.ENCAPS_PDF_MEDIA_SOP_INSTANCE_UID
    assert file_meta.ImplementationClassUID == uid.ENCAPS_PDF_IMPL_CLASS_UID


@pytest.mark.pdfencaps
def test_02_1_encapsulate_pdf(pdfencapsconverter):
    file_meta = pdfencapsconverter._get_encapspdf_meta()
    input_pdf_path = "tests/test_data/test_file.pdf"
    ds = pdfencapsconverter.encapsulate_pdf(file_meta, input_pdf_path)

    assert type(ds) == FileDataset
    assert len(ds.EncapsulatedDocument) == 898332
    assert ds.SOPClassUID == uid.ENCAPS_PDF_MEDIA_SOP_CLASS_UID
    assert ds.MIMETypeOfEncapsulatedDocument == "application/pdf"


@pytest.mark.pdfencaps
def test_02_2_end2end(pdfencapsconverter):
    path_pdf = "tests/test_data/test_file.pdf"
    ref_dicom = "tests/test_data/CT_small.dcm"

    # no personalisation
    stored_path = pdfencapsconverter.run(path_pdf)
    # check generation
    assert os.path.exists(stored_path)
    assert pdfencapsconverter.check_valid_dcm(stored_path)

    # check attribute
    dcm_ds = pydicom.dcmread(stored_path)
    assert len(dcm_ds.EncapsulatedDocument) == 898332

    os.remove(stored_path)

    # with personalisation
    stored_path = pdfencapsconverter.run(path_pdf, ref_dicom)
    assert os.path.exists(stored_path)
    assert pdfencapsconverter.check_valid_dcm(stored_path)

    dcm_ds = pydicom.dcmread(stored_path)
    # check repersonaliation attribute
    assert len(dcm_ds.EncapsulatedDocument) == 898332
    assert dcm_ds.PatientName == "CompressedSamples^CT1"
    assert dcm_ds.PatientID == "1CT1"
    assert dcm_ds.PatientSex == "O"

    os.remove(stored_path)

    # check no extension dcm creation
    stored_path = pdfencapsconverter.run(path_pdf, ref_dicom, suffix="")
    assert str(stored_path) == "tests/test_data/test_file"
    assert pdfencapsconverter.check_valid_dcm(stored_path)

    os.remove(stored_path)
