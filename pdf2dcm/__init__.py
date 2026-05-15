"""
Convert PDF files into DICOM objects.

Examples:
	Encapsulate a PDF into a DICOM file:

	from pdf2dcm import Pdf2EncapsDCM

	converter = Pdf2EncapsDCM()
	converter.run("example.pdf")

	Create RGB secondary capture DICOMs from a PDF:

	from pdf2dcm import Pdf2RgbSC

	converter = Pdf2RgbSC()
	converter.run("example.pdf")
"""

__version__ = "0.5.2"
from .pdf2encaps import Pdf2EncapsDCM  # noqa
from .pdf2rgb import Pdf2RgbSC  # noqa
