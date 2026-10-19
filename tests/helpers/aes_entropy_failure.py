import ctypes
import ctypes.util
import errno
import sys
import oxidize_pdf as p
strength = getattr(p.EncryptionStrength, sys.argv[1])
doc = p.Document()
page = p.Page.a4()
page.set_font(p.Font.HELVETICA, 12)
page.text_at(72, 700, 'entropy sentinel')
doc.add_page(page)
doc.encrypt('user', 'owner', strength=strength)
# Warm the thread-local RNG before denying fresh OS entropy for the IV.
doc.save_to_bytes()
lib = ctypes.CDLL(ctypes.util.find_library('seccomp'))
lib.seccomp_init.argtypes = [ctypes.c_uint32]
lib.seccomp_init.restype = ctypes.c_void_p
lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
lib.seccomp_load.argtypes = [ctypes.c_void_p]
lib.seccomp_release.argtypes = [ctypes.c_void_p]
ctx = lib.seccomp_init(0x7fff0000)
assert ctx
number = lib.seccomp_syscall_resolve_name(b'getrandom')
assert number >= 0
assert lib.seccomp_rule_add(ctx, 0x50000 | errno.EPERM, number, 0) == 0
assert lib.seccomp_load(ctx) == 0
lib.seccomp_release(ctx)
try:
    if len(sys.argv) > 2:
        doc.save(sys.argv[2])
    else:
        doc.save_to_bytes()
except p.PdfEncryptionError as e:
    assert 'secure entropy unavailable for AES IV' in str(e), repr(e)
    print(type(e).__name__, str(e))
else:
    raise AssertionError('Encryption succeeded without OS entropy')
