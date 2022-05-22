import pytest
import os

import pydicom


@pytest.mark.reperson
def test_03_1_full_personlisation(pdfencapsconverter):
    path_pdf = "tests/test_data/test_file.pdf"
    ref_dicom = "tests/test_data/CT_small.dcm"

    # with personalisation
    stored_path = pdfencapsconverter.run(path_pdf, ref_dicom)
    import pdb

    pdb.set_trace()
    assert os.path.exists(stored_path)
    assert pdfencapsconverter.check_valid_dcm(stored_path)

    dcm_ds = pydicom.dcmread(stored_path)
    ref_dcm_ds = pydicom.dcmread(ref_dicom)

    # check repersonaliation attribute
    assert len(dcm_ds.EncapsulatedDocument) == 898332
    assert dcm_ds.PatientName == ref_dcm_ds.PatientName
    assert dcm_ds.PatientID == ref_dcm_ds.PatientID
    assert dcm_ds.PatientSex == ref_dcm_ds.PatientSex

    os.remove(stored_path)


@pytest.mark.reperson
def test_03_2_uid_missing(pdfencapsconverter):
    path_pdf = "tests/test_data/test_file.pdf"
    ref_dicom = "tests/test_data/CT_small_no_UID.dcm"

    # with personalisation
    stored_path = pdfencapsconverter.run(path_pdf, ref_dicom)
    assert os.path.exists(stored_path)
    assert pdfencapsconverter.check_valid_dcm(stored_path)

    dcm_ds = pydicom.dcmread(stored_path)
    ref_dcm_ds = pydicom.dcmread(ref_dicom)

    # check repersonaliation attribute
    assert len(dcm_ds.EncapsulatedDocument) == 898332
    assert dcm_ds.PatientName == ref_dcm_ds.PatientName
    assert dcm_ds.PatientSex == ref_dcm_ds.PatientSex
    assert dcm_ds.SeriesInstanceUID[:6] == "1.9.9."

    os.remove(stored_path)
