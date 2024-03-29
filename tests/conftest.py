# add root-dir to sys path for tests
import sys
import pytest
from os.path import abspath
from os.path import dirname as d

parent_dir = f"{d(d(abspath(__file__)))}"
sys.path.append(parent_dir)

from pdf2dcm import Pdf2EncapsDCM, Pdf2RgbSC  # noqa


@pytest.fixture
def baseconverter():
    yield Pdf2EncapsDCM()


@pytest.fixture
def pdfencapsconverter():
    yield Pdf2EncapsDCM()


@pytest.fixture
def rgbscconverter():
    yield Pdf2RgbSC()

@pytest.fixture
def pdfrepersonconverter():
    yield Pdf2EncapsDCM(repersonalisation_fields=[
        "PatientName",
        "PatientID",
        "PatientSex",
        "StudyInstanceUID",
        "AccessionNumber"
    ])