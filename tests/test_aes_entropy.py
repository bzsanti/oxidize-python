"""Published-core AES contract, checked through Python and independent qpdf."""
import ctypes.util
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import oxidize_pdf as p


@pytest.mark.parametrize('strength', ['AES_128', 'AES_256'])
def test_aes_ciphertext_and_independent_decryption(strength, tmp_path):
    if not shutil.which('qpdf'):
        pytest.skip('independent qpdf reader unavailable')
    doc = p.Document()
    page = p.Page.a4()
    page.set_font(p.Font.HELVETICA, 12)
    page.text_at(72, 700, 'AES-550-secret-sentinel')
    doc.add_page(page)
    doc.encrypt('user', 'owner', strength=getattr(p.EncryptionStrength, strength))
    encrypted = tmp_path / 'encrypted.pdf'
    encrypted.write_bytes(doc.save_to_bytes())
    assert b'AES-550-secret-sentinel' not in encrypted.read_bytes()
    decrypted = tmp_path / 'decrypted.pdf'
    subprocess.run(['qpdf', '--password=user', '--decrypt', '--qdf', '--object-streams=disable', str(encrypted), str(decrypted)], check=True, capture_output=True)
    assert b'AES-550-secret-sentinel' in decrypted.read_bytes()
    rejected = subprocess.run(['qpdf', '--password=wrong', '--check', str(encrypted)], capture_output=True)
    assert rejected.returncode != 0
    assert b'invalid password' in rejected.stderr


@pytest.mark.skipif(sys.platform != 'linux' or not ctypes.util.find_library('seccomp'), reason='fault injection requires Linux libseccomp')
@pytest.mark.parametrize('strength', ['AES_128', 'AES_256'])
@pytest.mark.parametrize('output', ['bytes', 'file'])
def test_aes_entropy_failure_is_python_error_without_valid_output(strength, output, tmp_path):
    """Deny OS entropy only in a child; exercise the actual native extension."""
    path = tmp_path / 'failed.pdf'
    command = [sys.executable, str(Path(__file__).parent / 'helpers/aes_entropy_failure.py'), strength]
    if output == 'file':
        command.append(str(path))
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PdfEncryptionError' in result.stdout
    assert 'secure entropy unavailable for AES IV' in result.stdout
    if path.exists():
        assert b'%%EOF' not in path.read_bytes()
        if shutil.which('qpdf'):
            checked = subprocess.run(['qpdf', '--password=user', '--check', str(path)], capture_output=True)
            assert checked.returncode == 2, checked.stdout + checked.stderr


@pytest.mark.parametrize('strength', ['AES_128', 'AES_256'])
def test_aes_round_trip_on_each_platform(strength):
    doc = p.Document()
    page = p.Page.a4()
    page.set_font(p.Font.HELVETICA, 12)
    page.text_at(72, 700, 'AES-platform-sentinel')
    doc.add_page(page)
    doc.encrypt('user', 'owner', strength=getattr(p.EncryptionStrength, strength))
    data = doc.save_to_bytes()
    assert b'AES-platform-sentinel' not in data
    reader = p.PdfReader.from_bytes(data)
    with pytest.raises(p.PdfEncryptionError):
        reader.extract_text()
    with pytest.raises(p.PdfEncryptionError):
        reader.unlock('wrong')
    reader.unlock('user')
    assert 'AES-platform-sentinel' in ''.join(reader.extract_text())
