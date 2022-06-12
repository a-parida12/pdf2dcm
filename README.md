# pdf2dcm
[![PyPI version](https://img.shields.io/pypi/v/pdf2dcm.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/pdf2dcm/) [![Supported Python versions](https://img.shields.io/pypi/pyversions/pdf2dcm.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/pdf2dcm)[![Downloads](https://static.pepy.tech/personalized-badge/pdf2dcm?period=month&units=abbreviation&left_color=brightgreen&right_color=blue&left_text=PyPi%20Velocity)](https://pepy.tech/project/pdf2dcm) [![Downloads](https://static.pepy.tech/personalized-badge/pdf2dcm?period=total&units=abbreviation&left_color=brightgreen&right_color=blue&left_text=PyPi%20Downloads)](https://pepy.tech/project/pdf2dcm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![codecov](https://codecov.io/gh/a-parida12/pdf2dcm/branch/main/graph/badge.svg?token=MGY9MHRP46)](https://codecov.io/gh/a-parida12/pdf2dcm)[![Test Pipeline](https://github.com/a-parida12/pdf2dcm/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/a-parida12/pdf2dcm/actions/workflows/test.yml)[![Release Pipeline](https://github.com/a-parida12/pdf2dcm/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/a-parida12/pdf2dcm/actions/workflows/release.yml)

PDF to DICOM Converter

> A python package for PDF to Encapsulated DCM and PDF to DICOM RGB converter

## SETUP

### Python Package Setup

The python package is available for use on PyPI. It can be setup simply via pip

```bash
pip install pdf2dcm
```

To the check the setup, simply check the version number of the `pdf2dcm` package by

```bash
python -c 'import pdf2dcm; print(pdf2dcm.__version__)'
```

### Poppler Setup
Poppler is a popular project that is used for the creation of Dicom RGB Secondary Capture. You can check if you already have it installed by calling `pdftoppm -h` in your terminal/cmd. To install poppler these are some of the recommended ways-

Conda
```bash
conda install -c conda-forge poppler
```

Ubuntu
```bash
sudo apt-get install poppler-utils
```

MacOS
```bash
brew install poppler
```

## PDF to Encapsulated DCM

### Usage

```python
from pdf2dcm import Pdf2EncapsDCM

converter = Pdf2EncapsDCM()
converted_dcm = converter.run(path_pdf='tests/test_data/test_file.pdf', path_template_dcm='tests/test_data/CT_small.dcm', suffix =".dcm")
print(converted_dcm)
# [ 'tests/test_data/test_file.dcm' ]
```

Parameters `converter.run`:

- `path_pdf (str)`: path of the pdf that needs to be encapsulated
- `path_template_dcm (str, optional)`: path to template for getting the repersonalisation of data.
- `suffix (str, optional)`: suffix of the dicom files. Defaults to ".dcm".

Returns:

- `List[Path]`: list of path of the stored encapsulated dcm

## PDF to RGB Secondary Capture DCM

### Usage

```python
from pdf2dcm import Pdf2RgbSC

converter = Pdf2RgbSC()
converted_dcm = converter.run(path_pdf='tests/test_data/test_file.pdf', path_template_dcm='tests/test_data/CT_small.dcm', suffix =".dcm")
print(converted_dcm)
# [ 'tests/test_data/test_file_0.dcm', 'tests/test_data/test_file_1.dcm' ]
```

Parameters `converter.run`:

- `path_pdf (str)`: path of the pdf that needs to be converted
- `path_template_dcm (str, optional)`: path to template for getting the repersonalisation of data.
- `suffix (str, optional)`: suffix of the dicom files. Defaults to ".dcm".

Returns:

- `List[Path]`: list of paths of the stored secondary capture dcm
## Notes

- The name of the output dicom is same as the name of the input pdf
- If no template is provided no repersonalisation takes place
- It is possible to produce dicoms without a suffix by simply passing `suffix=""` to the `converter.run()`

## Repersonalisation

It is the process of copying over data regarding the identity of the encapsualted pdf from a template dicom. Currently, the fileds that are repersonalised are-

- PatientName
- PatientID
- PatientSex
- StudyInstanceUID
- SeriesInstanceUID
- SOPInstanceUID
