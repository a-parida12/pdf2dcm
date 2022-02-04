import pytest
import os
import pydicom
from pydicom.dataset import FileMetaDataset, FileDataset


@pytest.mark.base
def test_01_1_get_dicom_meta(baseconverter):
    ds = baseconverter._get_dicom_meta()
    assert type(ds) == FileMetaDataset
    assert ds.ImplementationVersionName == "pdf2dcm"


@pytest.mark.base
def test_01_2_get_dicom_body(baseconverter):
    meta = FileMetaDataset()
    ds = baseconverter._get_dicom_body(meta)

    assert type(ds) == FileDataset
    assert type(ds.ContentTime) == str
    assert ds.Modality == "DOC"
    assert ds.ConversionType == "WSD"


@pytest.mark.base
def test_01_3_check_dcm(baseconverter):
    not_dicom_path = "tests/test_data/test_file.pdf"
    dicom_path = "tests/test_data/CT_small.dcm"

    assert type(baseconverter.check_valid_dcm(not_dicom_path)) == bool
    assert not baseconverter.check_valid_dcm(not_dicom_path)
    assert baseconverter.check_valid_dcm(dicom_path)


def test_01_4_save_dcm(baseconverter):
    dicom_path = "tests/test_data/CT_small.dcm"
    ds = pydicom.dcmread(dicom_path, defer_size=1024)
    out_dicom_path = "tests/test_data/test.dcm"
    out_path = baseconverter._store_ds(out_dicom_path, ds)

    assert out_path == out_dicom_path
    assert os.path.exists(out_path)

    os.remove(out_path)
