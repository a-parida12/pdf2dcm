from .base import BaseConverter
from .utils import uid
from pathlib import Path
from typing import List
import os
from pydicom.dataset import FileMetaDataset, FileDataset
from pydicom.uid import generate_uid
from pdf2image import convert_from_path
from copy import deepcopy
from PIL import Image


class Pdf2RgbSC(BaseConverter):
    def __init__(self, dpi=144, merge_pages=False):
        """Class for the generation RGB Secondary capture

        Args:
            dpi (int, optional): dots per inch, set resolution of the image. Defaults to 144.
            merge_pages (bool, optional): multiple pgs must be put into 1 dicom. Defaults to False.
        """
        self.merge_pages_flag = merge_pages
        self.dpi = dpi
        super().__init__()

    def _get_rgbsc_meta(self) -> FileMetaDataset:
        """Get and set the file meta information for the rgb secondary capture dicom

        Returns:
            FileMetaDataset: header meta info of the dicom
        """
        # get generic meta information
        file_meta = self._get_dicom_meta()

        # set rgb sc specific uids from the uid list
        file_meta.MediaStorageSOPClassUID = uid.RGB_SC_MEDIA_SOP_CLASS_UID
        file_meta.MediaStorageSOPInstanceUID = uid.RGB_SC_MEDIA_SOP_INSTANCE_UID
        file_meta.ImplementationClassUID = uid.RGB_SC_IMPL_CLASS_UID
        return file_meta

    def generate_rgb_sc(self, file_meta: FileMetaDataset, img, frameID) -> FileDataset:
        """method to rgb sc pdf byte stream in a dicom

        Args:
            file_meta (FileMetaDataset): meta information of a dicom
            img (PIL Image): A PIL type rgb image to be stored as RGB SC Dicom
            frameID (int): integer value of frameID to return pages in single series

        Returns:
            FileDataset: rgb sc dicom dataset
        """
        ds = self._get_dicom_body(deepcopy(file_meta))
        ds.SOPClassUID = uid.RGB_SC_MEDIA_SOP_CLASS_UID

        ds.PhotometricInterpretation = "RGB"
        ds.SamplesPerPixel = 3
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.Rows = img.size[1]
        ds.Columns = img.size[0]
        ds.add_new(0x00280006, "US", 0)
        ds.InstanceNumber = frameID+1

        ds.PixelData = img.tobytes()
        ds.PixelRepresentation = 0
        ds.LargestImagePixelValue = 255
        ds.SmallestImagePixelValue = 0

        return ds

    def merge_pages(self, pages: list) -> list:
        """method to horizontally stack the pages of a report

        Args:
            pages (list): list of Pil images that needs to bestacked

        Returns:
            list: list with one element of teh stacked imges
        """
        widths, heights = zip(*(i.size for i in pages))
        width = max(widths)
        height = sum(heights)
        new_im = Image.new("RGB", (width, height))
        y_offset = 0
        for im in pages:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]

        return [new_im]

    def run(
        self,
        path_pdf: str,
        path_template_dcm: str = "",
        suffix: str = ".dcm",
    ) -> List[Path]:
        """Run the complete secondary capture creation procedure on a given a pdf

        Args:
            path_pdf (str): path of the pdf that needs to be converted
            path_template_dcm (str, optional): path to template for getting the
                                               repersonalisation of data.
            suffix (str, optional): suffix of the dicom files. Defaults to ".dcm".

        Returns:
            List[Path]: list of paths of the stored secondary capture dcm
        """

        # convert to path type
        path_pdf_path = Path(path_pdf)
        path_template_dcm_path = Path(path_template_dcm)
        dicom_pdf_file_paths = []

        # personalisation
        personalisation = path_template_dcm_path != Path("") and self.check_valid_dcm(
            path_template_dcm_path
        )

        # get file meta
        rgbsc_meta = self._get_rgbsc_meta()

        # pdf pages as images
        pages = convert_from_path(path_pdf_path, dpi=self.dpi)

        if self.merge_pages_flag:
            pages = self.merge_pages(pages)

        # store path
        name = path_pdf_path.stem
        path = path_pdf_path.parent
        
        seriesUID = generate_uid()
        for idx, page in enumerate(pages):
            store_dcm_path = Path(os.path.join(path, f"{name}_{idx}{suffix}"))
            rgb_sc_dcm = self.generate_rgb_sc(rgbsc_meta, page, idx)
            if personalisation:
                rgb_sc_dcm = self.personalize_dcm(path_template_dcm_path, rgb_sc_dcm)
            rgb_sc_dcm.SeriesInstanceUID = seriesUID
            dicom_pdf_file_paths.append(self._store_ds(store_dcm_path, rgb_sc_dcm))

        return dicom_pdf_file_paths
