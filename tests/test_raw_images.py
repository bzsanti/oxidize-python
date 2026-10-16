"""Packed pixel input and image inspection against serialized PDF image streams."""
import re
import shutil
import subprocess
import zlib
import pytest
import oxidize_pdf as p
from helpers import _minimal_jpeg, _minimal_png

CS = p.ImageColorSpace


def pdf_with_image(image):
    page = p.Page(30, 10)
    page.add_image('pixels', image)
    page.draw_image('pixels', 0, 0, 30, 10)
    document = p.Document()
    document.add_page(page)
    return document.save_to_bytes()


def image_streams(pdf):
    # Independent inspection of the writer's classic-xref output.
    result = []
    for match in re.finditer(rb'\d+ 0 obj\s*(.*?)\s*endobj', pdf, re.S):
        body = match[1]
        if b'/Subtype /Image' not in body or b'\nstream\n' not in body:
            continue
        header, stream = body.split(b'\nstream\n', 1)
        length = int(re.search(rb'/Length\s+(\d+)', header)[1])
        payload = stream[:length]
        if b'/FlateDecode' in header:
            payload = zlib.decompress(payload)
        result.append((header, payload))
    assert result, 'No PDF image streams found'
    return result


@pytest.mark.parametrize('space,bits,width,height,pixels,pdf_space', [
    (CS.DeviceRGB, 8, 2, 1, bytes([255, 0, 0, 0, 255, 0]), b'DeviceRGB'),
    (CS.DeviceCMYK, 8, 1, 1, bytes([0, 255, 0, 0]), b'DeviceCMYK'),
    (CS.DeviceGray, 8, 2, 1, bytes([0, 255]), b'DeviceGray'),
    (CS.DeviceGray, 1, 3, 2, bytes([0b10100000, 0b01000000]), b'DeviceGray'),
    (CS.DeviceGray, 2, 3, 2, bytes([0b00011000, 0b11100100]), b'DeviceGray'),
    (CS.DeviceGray, 4, 1, 2, bytes([0x10, 0xf0]), b'DeviceGray'),
    (CS.DeviceRGB, 16, 1, 1, bytes([0xff, 0xff, 0, 0, 0x80, 0]), b'DeviceRGB'),
])
def test_raw_scanlines_preserve_color_depth_and_bytes(space, bits, width, height, pixels, pdf_space):
    image = p.Image.from_raw_data(pixels, width, height, space, bits)
    assert (image.width, image.height, image.bits_per_component) == (width, height, bits)
    assert image.format == p.ImageFormat.Raw and image.data == pixels
    assert image.alpha_data is None and image.soft_mask is None and not image.has_transparency
    header, payload = image_streams(pdf_with_image(image))[0]
    assert b'/ColorSpace /' + pdf_space in header
    assert b'/BitsPerComponent ' + str(bits).encode() in header
    assert b'/Width ' + str(width).encode() in header and b'/Height ' + str(height).encode() in header
    assert payload == pixels


def test_rgba_split_soft_mask_and_owned_snapshots():
    rgba = bytes([255, 0, 0, 255, 0, 255, 0, 128, 0, 0, 255, 0])
    image = p.Image.from_rgba_data(rgba, 3, 1)
    assert image.data == bytes([255, 0, 0, 0, 255, 0, 0, 0, 255])
    assert image.alpha_data == bytes([255, 128, 0]) and image.has_transparency
    mask = image.soft_mask
    assert mask is not None and mask.data == image.alpha_data
    assert (mask.width, mask.height, mask.bits_per_component) == (3, 1, 8)
    assert mask.format == p.ImageFormat.Raw and mask.soft_mask is None and mask.alpha_data is None
    with pytest.raises(AttributeError):
        image.data = b'changed'
    del image
    assert mask.data == bytes([255, 128, 0])
    image = p.Image.from_rgba_data(rgba, 3, 1)
    streams = image_streams(pdf_with_image(image))
    rgb = [(h, data) for h, data in streams if b'/DeviceRGB' in h]
    gray = [(h, data) for h, data in streams if b'/DeviceGray' in h]
    assert len(rgb) == len(gray) == 1
    assert b'/SMask ' in rgb[0][0]
    assert rgb[0][1] == image.data and gray[0][1] == image.alpha_data


def test_gray_constructor_and_existing_format_getters():
    gray = p.Image.from_gray_data(bytes([7, 128, 251]), 3, 1)
    assert gray.data == bytes([7, 128, 251]) and gray.bits_per_component == 8
    assert gray.format == p.ImageFormat.Raw and not gray.has_transparency
    assert b'/DeviceGray' in image_streams(pdf_with_image(gray))[0][0]
    jpeg_bytes = _minimal_jpeg()
    jpeg = p.Image.from_jpeg_data(jpeg_bytes)
    assert jpeg.format == p.ImageFormat.Jpeg and jpeg.data == jpeg_bytes
    png = p.Image.from_png_data(_minimal_png())
    assert png.format == p.ImageFormat.Png and png.data != _minimal_png()
    assert len(png.data) == png.width * png.height * 3


@pytest.mark.parametrize('factory,channels', [(p.Image.from_rgba_data, 4), (p.Image.from_gray_data, 1)])
@pytest.mark.parametrize('width,height', [(0, 1), (1, 0), (1 << 31, 2), (65536, 65536)])
def test_checked_core_dimensions(factory, channels, width, height):
    with pytest.raises(ValueError, match='dimensions'):
        factory(b'', width, height)
    assert factory(bytes(channels), 1, 1).width == 1


@pytest.mark.parametrize('bits', [0, 3, 7, 12, 32, 255])
def test_invalid_bit_depth(bits):
    with pytest.raises(ValueError, match='bits_per_component'):
        p.Image.from_raw_data(b'\x00', 1, 1, CS.DeviceGray, bits)


@pytest.mark.parametrize('factory,args', [
    (p.Image.from_rgba_data, (b'123', 1, 1)),
    (p.Image.from_gray_data, (b'12', 1, 1)),
    (p.Image.from_raw_data, (b'123', 2, 1, CS.DeviceRGB)),
    (p.Image.from_raw_data, (b'\xa8', 3, 2, CS.DeviceGray, 1)),
    (p.Image.from_raw_data, (b'', 0, 2, CS.DeviceRGB)),
    (p.Image.from_raw_data, (b'', 2**32 - 1, 2**32 - 1, CS.DeviceCMYK, 16)),
])
def test_invalid_buffers_rejected_before_core(factory, args):
    with pytest.raises(ValueError, match='size|dimensions'):
        factory(*args)


@pytest.mark.parametrize('value', [-1, 2**32])
def test_unsigned_dimensions(value):
    with pytest.raises(OverflowError):
        p.Image.from_gray_data(b'', value, 1)
    with pytest.raises(OverflowError):
        p.Image.from_rgba_data(b'', 1, value)
    with pytest.raises(OverflowError):
        p.Image.from_raw_data(b'', value, 1, CS.DeviceGray)


@pytest.mark.skipif(not all(shutil.which(tool) for tool in ('qpdf', 'pdftoppm')), reason='independent PDF tools unavailable')
def test_poppler_pixels_and_alpha(tmp_path):
    image = p.Image.from_rgba_data(bytes([255, 0, 0, 255, 0, 255, 0, 128, 0, 0, 255, 0]), 3, 1)
    path = tmp_path / 'rgba.pdf'
    path.write_bytes(pdf_with_image(image))
    subprocess.run(['qpdf', '--check', str(path)], check=True, capture_output=True)
    ppm = subprocess.run(['pdftoppm', '-r', '72', '-singlefile', str(path)], check=True, capture_output=True).stdout
    match = re.match(rb'P6\s+(\d+)\s+(\d+)\s+255\s', ppm)
    assert match is not None and (int(match[1]), int(match[2])) == (30, 10)
    pixels = ppm[match.end():]
    assert len(pixels) == 30 * 10 * 3
    def pixel(x):
        start = (5 * 30 + x) * 3
        return tuple(pixels[start:start + 3])
    assert pixel(5) == (255, 0, 0)
    assert pixel(25) == (255, 255, 255)
    red, green, blue = pixel(15)
    assert 126 <= red <= 128 and green == 255 and 126 <= blue <= 128
