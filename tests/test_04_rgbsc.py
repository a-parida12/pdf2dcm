import pytest
import os

from pdf2dcm.utils import uid
import pydicom
from pydicom.dataset import FileMetaDataset, FileDataset
from pdf2image import convert_from_path


@pytest.mark.rgbsc
def test_04_1_get_rgbsc_meta(rgbscconverter):
    file_meta = rgbscconverter._get_rgbsc_meta()

    assert type(file_meta) == FileMetaDataset
    assert file_meta.MediaStorageSOPClassUID == uid.RGB_SC_MEDIA_SOP_CLASS_UID
    assert file_meta.MediaStorageSOPInstanceUID == uid.RGB_SC_MEDIA_SOP_INSTANCE_UID
    assert file_meta.ImplementationClassUID == uid.RGB_SC_IMPL_CLASS_UID


@pytest.mark.rgbsc
def test_04_2_generate_rgb_sc(rgbscconverter):
    file_meta = rgbscconverter._get_rgbsc_meta()
    input_pdf_path = "tests/test_data/test_rgb.pdf"
    images = convert_from_path(input_pdf_path, dpi=144)
    ds = rgbscconverter.generate_rgb_sc(file_meta, images[0])

    assert type(ds) == FileDataset
    assert len(ds.PixelData) == 5816448
    assert ds.SOPClassUID == uid.RGB_SC_MEDIA_SOP_CLASS_UID


@pytest.mark.rgbsc
def test_04_3_end2end(rgbscconverter):
    path_pdf = "tests/test_data/test_rgb.pdf"
    ref_dicom = "tests/test_data/CT_small.dcm"

    # no personalisation
    stored_paths = rgbscconverter.run(path_pdf)

    # check generation
    for path in stored_paths:
        assert os.path.exists(path)
        assert rgbscconverter.check_valid_dcm(path)

        # check attribute
        dcm_ds = pydicom.dcmread(path)
        assert len(dcm_ds.PixelData) == 5816448

        os.remove(path)

    # with personalisation
    stored_paths = rgbscconverter.run(path_pdf, ref_dicom)

    # check generation
    for path in stored_paths:
        assert os.path.exists(path)
        assert rgbscconverter.check_valid_dcm(path)

        # check attribute
        dcm_ds = pydicom.dcmread(path)
        assert len(dcm_ds.PixelData) == 5816448
        assert dcm_ds.PatientName == "CompressedSamples^CT1"
        assert dcm_ds.PatientID == "1CT1"
        assert dcm_ds.PatientSex == "O"

        os.remove(path)

    # check no extension dcm creation
    stored_paths = rgbscconverter.run(path_pdf, ref_dicom, suffix="")

    for i, path in enumerate(stored_paths):
        assert str(path) == f"tests/test_data/test_rgb_{i}"
        assert rgbscconverter.check_valid_dcm(path)
        os.remove(path)
