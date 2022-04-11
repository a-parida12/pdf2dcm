# pdf2dcm
[![Python Application Testing](https://github.com/a-parida12/pdf2dcm/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/a-parida12/pdf2dcm/actions/workflows/test.yml)[![Test and Release](https://github.com/a-parida12/pdf2dcm/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/a-parida12/pdf2dcm/actions/workflows/release.yml)

PDF to DICOM Converter

> A python package for PDF to Encapsulated DCM and PDF to DICOM RGB converter

## SETUP

The python package is available for use on PyPI. It can be setup simply via pip

```bash
pip install pdf2dcm
```

To the check the setup, simply check the version number of the `pdf2dcm` package by

```bash
python -c 'import pdf2dcm; print(pdf2dcm.__version__)'
```

## PDF to Encapsulated DCM

### Usage

```python
from pdf2dcm import Pdf2EncapsDCM

converter = Pdf2EncapsDCM()
converted_dcm = converter.run(path_pdf='tests/test_data/test_file.pdf', path_template_dcm='tests/test_data/CT_small.dcm', suffix =".dcm")
print(converted_dcm)
# tests/test_data/test_file'
```

Parameters `converter.run`:

- `path_pdf (str)`: path of the pdf that needs to be encapsulated
- `path_template_dcm (str, optional)`: path to template for getting the repersonalisation of data.
- `suffix (str, optional)`: suffix of the dicom files. Defaults to ".dcm".

Returns:

- `Path`: path of the stored encapsulated dcm

### Notes

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
