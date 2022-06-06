import datetime


def generate_random_uid() -> str:
    """Generate a dicom compatible UID

    Returns:
        [str]: the generated UId based on date and time
    """
    return "1.9.9." + str(datetime.datetime.now().strftime("%H%M%S%f%d%m%Y"))


# Encapsulated PDF
ENCAPS_PDF_MEDIA_SOP_CLASS_UID = "1.2.840.10008.5.1.4.1.1.104.1"
ENCAPS_PDF_MEDIA_SOP_INSTANCE_UID = "1.2.276.0.7230010.3.1.4.0.52431.1531080773.369825"
ENCAPS_PDF_IMPL_CLASS_UID = "1.2.276.0.7230010.3.0.3.6.3"

# RGB Secondary Capture PDF
RGB_SC_MEDIA_SOP_CLASS_UID = "1.2.840.10008.5.1.4.1.1.7"
RGB_SC_MEDIA_SOP_INSTANCE_UID = "1.2.276.0.116.2485377957891.1.1621350463859.0.3"
RGB_SC_IMPL_CLASS_UID = "1.2.276.0.116.1.3.4.1"
