import pytest
from pdf2dcm.utils.uid import (
    ENCAPS_PDF_MEDIA_SOP_CLASS_UID,
    ENCAPS_PDF_MEDIA_SOP_INSTANCE_UID,
    ENCAPS_PDF_IMPL_CLASS_UID,
)


@pytest.mark.utils
def test_00_2_check_const_uid():
    assert type(ENCAPS_PDF_MEDIA_SOP_CLASS_UID) == str
    assert type(ENCAPS_PDF_MEDIA_SOP_INSTANCE_UID) == str
    assert type(ENCAPS_PDF_IMPL_CLASS_UID) == str
