use std::ffi::{c_int, c_uint, c_ulong, c_void};
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};

static DENIED: AtomicBool = AtomicBool::new(false);
static FAILURES: AtomicUsize = AtomicUsize::new(0);

#[link(name = "dl")]
extern "C" {
    fn dlsym(handle: *mut c_void, symbol: *const u8) -> *mut c_void;
    fn __errno_location() -> *mut c_int;
}

#[no_mangle]
pub extern "C" fn entropy_test_deny() {
    DENIED.store(true, Ordering::SeqCst);
}

#[no_mangle]
pub extern "C" fn entropy_test_failures() -> c_ulong {
    FAILURES.load(Ordering::SeqCst) as c_ulong
}

#[no_mangle]
pub unsafe extern "C" fn getrandom(buffer: *mut c_void, length: usize, flags: c_uint) -> isize {
    if DENIED.load(Ordering::SeqCst) {
        FAILURES.fetch_add(1, Ordering::SeqCst);
        // Linux EPERM. No bytes are written on the denied path.
        *__errno_location() = 1;
        return -1;
    }
    // RTLD_NEXT preserves the platform's normal libc entropy path until armed.
    let next = dlsym(-1isize as *mut c_void, b"getrandom\0".as_ptr());
    if next.is_null() {
        *__errno_location() = 38; // Linux ENOSYS.
        return -1;
    }
    let next: unsafe extern "C" fn(*mut c_void, usize, c_uint) -> isize = std::mem::transmute(next);
    next(buffer, length, flags)
}
