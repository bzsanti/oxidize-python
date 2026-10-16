from oxidize_pdf import Image, ImageColorSpace, ImageFormat, Page


def pixels() -> bytes:
    rgb = Image.from_raw_data(b'\xff\x00\x00', 1, 1, ImageColorSpace.DeviceRGB)
    gray = Image.from_gray_data(b'\x80', 1, 1)
    rgba = Image.from_rgba_data(b'\xff\x00\x00\x80', 1, 1)
    packed = Image.from_raw_data(b'\x80', 1, 1, ImageColorSpace.DeviceGray, 1)
    cmyk = Image.from_raw_data(b'\x00\xff\x00\x00', 1, 1, ImageColorSpace.DeviceCMYK, 8)
    encoding: ImageFormat = rgb.format
    bits: int = packed.bits_per_component
    alpha: bytes | None = rgba.alpha_data
    mask: Image | None = rgba.soft_mask
    assert encoding == ImageFormat.Raw and bits == 1 and alpha is not None
    assert mask is not None and mask.data == alpha
    page = Page.a4()
    for index, image in enumerate([rgb, gray, rgba, packed, cmyk]):
        page.add_image(str(index), image)
        page.draw_image(str(index), 0, 0, image.width, image.height)
    return rgb.data
