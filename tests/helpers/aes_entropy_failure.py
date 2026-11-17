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
# Cover libc's user-space entropy path as well as direct getrandom syscalls.
process = ctypes.CDLL(None, use_errno=True)
process.entropy_test_deny.argtypes = []
process.entropy_test_deny.restype = None
process.entropy_test_failures.argtypes = []
process.entropy_test_failures.restype = ctypes.c_ulong
process.getrandom.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint]
process.getrandom.restype = ctypes.c_ssize_t
probe = ctypes.create_string_buffer(16)
assert process.getrandom(probe, len(probe), 0) == len(probe)
assert process.entropy_test_failures() == 0
process.entropy_test_deny()
assert process.getrandom(probe, len(probe), 0) == -1
assert ctypes.get_errno() == errno.EPERM
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
before = process.entropy_test_failures()
try:
    if len(sys.argv) > 2:
        doc.save(sys.argv[2])
    else:
        doc.save_to_bytes()
except p.PdfEncryptionError as e:
    assert 'secure entropy unavailable for AES IV' in str(e), repr(e)
    assert process.entropy_test_failures() > before, 'native AES did not reach the injected libc boundary'
    print(type(e).__name__, str(e))
else:
    raise AssertionError('Encryption succeeded without OS entropy')
