import pytest
import os

import pydicom
from pydicom.uid import UID

from pdf2dcm import Pdf2EncapsDCM


@pytest.mark.reperson
def test_03_1_full_personlisation(pdfencapsconverter):
    path_pdf = "tests/test_data/test_file.pdf"
    ref_dicom = "tests/test_data/CT_small.dcm"

    # with personalisation
    stored_path = pdfencapsconverter.run(path_pdf, ref_dicom)[0]

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
    stored_path = pdfencapsconverter.run(path_pdf, ref_dicom)[0]
    assert os.path.exists(stored_path)
    assert pdfencapsconverter.check_valid_dcm(stored_path)

    dcm_ds = pydicom.dcmread(stored_path)
    ref_dcm_ds = pydicom.dcmread(ref_dicom)

    # check repersonaliation attribute
    assert len(dcm_ds.EncapsulatedDocument) == 898332
    assert dcm_ds.PatientName == ref_dcm_ds.PatientName

    # check the randomly generated uid
    # assert type(dcm_ds.SeriesInstanceUID[:6]) == str

    os.remove(stored_path)


@pytest.mark.reperson
def test_03_2_name_missing(pdfencapsconverter):
    path_pdf = "tests/test_data/test_file.pdf"
    ref_dicom = "tests/test_data/CT_small_no_name.dcm"

    # with personalisation
    with pytest.warns(UserWarning, match="PatientName not found in DICOM"):
        stored_path = pdfencapsconverter.run(path_pdf, ref_dicom)[0]
    assert os.path.exists(stored_path)
    assert pdfencapsconverter.check_valid_dcm(stored_path)

    dcm_ds = pydicom.dcmread(stored_path)
    ref_dcm_ds = pydicom.dcmread(ref_dicom)

    # check repersonaliation attribute
    assert len(dcm_ds.EncapsulatedDocument) == 898332
    assert dcm_ds.StudyInstanceUID == ref_dcm_ds.StudyInstanceUID

    # check the empty field
    assert dcm_ds.PatientName == ""

    os.remove(stored_path)


@pytest.mark.reperson
def test_03_4_additional_fields_personlisation(pdfrepersonconverter):
    path_pdf = "tests/test_data/test_file.pdf"
    ref_dicom = "tests/test_data/CT_small_accession_number.dcm"

    # with personalisation
    stored_path = pdfrepersonconverter.run(path_pdf, ref_dicom)[0]

    assert os.path.exists(stored_path)
    assert pdfrepersonconverter.check_valid_dcm(stored_path)

    dcm_ds = pydicom.dcmread(stored_path)
    ref_dcm_ds = pydicom.dcmread(ref_dicom)

    # check repersonaliation attribute
    assert len(dcm_ds.EncapsulatedDocument) == 898332
    assert dcm_ds.PatientName == ref_dcm_ds.PatientName
    assert dcm_ds.PatientID == ref_dcm_ds.PatientID
    assert dcm_ds.PatientSex == ref_dcm_ds.PatientSex
    assert dcm_ds.AccessionNumber == ref_dcm_ds.AccessionNumber

    os.remove(stored_path)


@pytest.mark.reperson
def test_03_5_missing_fields_use_dictionary_vr(tmp_path):
    fields = [
        "PatientName",
        "PatientID",
        "PatientSex",
        "StudyInstanceUID",
        "AccessionNumber",
        "Rows",
    ]
    converter = Pdf2EncapsDCM(repersonalisation_fields=fields)
    template_dcm = pydicom.dcmread("tests/test_data/CT_small.dcm")
    for field in fields:
        del template_dcm[field]

    template_path = tmp_path / "missing_fields.dcm"
    template_dcm.save_as(template_path)
    output_dcm = converter._get_dicom_body(converter._get_dicom_meta())

    with pytest.warns(UserWarning) as warning_records:
        personalized_dcm = converter.personalize_dcm(template_path, output_dcm)

    expected_vrs = {
        "PatientName": "PN",
        "PatientID": "LO",
        "PatientSex": "CS",
        "StudyInstanceUID": "UI",
        "AccessionNumber": "SH",
        "Rows": "US",
    }
    for field, expected_vr in expected_vrs.items():
        assert personalized_dcm.data_element(field).VR == expected_vr

    assert personalized_dcm.PatientName == ""
    assert personalized_dcm.PatientID == ""
    assert personalized_dcm.PatientSex == ""
    assert personalized_dcm.AccessionNumber == ""
    assert personalized_dcm.Rows is None
    assert UID(personalized_dcm.StudyInstanceUID).is_valid

    warning_messages = [str(record.message) for record in warning_records]
    assert len(warning_records) == len(fields)
    for field, warning_message in zip(fields, warning_messages):
        assert f"{field} not found in DICOM {template_path}" in warning_message

    uid_warning = warning_messages[fields.index("StudyInstanceUID")]
    assert "using randomly generated values!" in uid_warning

    for field in ("PatientName", "PatientID", "PatientSex", "AccessionNumber", "Rows"):
        field_warning = warning_messages[fields.index(field)]
        assert "leaving the field empty!" in field_warning


@pytest.mark.reperson
def test_03_6_unknown_repersonalisation_field_raises_value_error():
    converter = Pdf2EncapsDCM(repersonalisation_fields=["NotARealDicomKeyword"])
    output_dcm = converter._get_dicom_body(converter._get_dicom_meta())

    with pytest.raises(ValueError, match="Unknown DICOM keyword: NotARealDicomKeyword"):
        converter.personalize_dcm("tests/test_data/CT_small.dcm", output_dcm)
