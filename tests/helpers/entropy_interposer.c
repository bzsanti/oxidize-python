#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <stdatomic.h>
#include <stddef.h>
#include <sys/types.h>

static atomic_int denied;
static atomic_ulong failures;

void entropy_test_deny(void) { atomic_store(&denied, 1); }
unsigned long entropy_test_failures(void) { return atomic_load(&failures); }

ssize_t getrandom(void *buffer, size_t length, unsigned int flags) {
    if (atomic_load(&denied)) {
        atomic_fetch_add(&failures, 1);
        errno = EPERM;
        return -1;
    }
    ssize_t (*next)(void *, size_t, unsigned int) = dlsym(RTLD_NEXT, "getrandom");
    if (!next) {
        errno = ENOSYS;
        return -1;
    }
    return next(buffer, length, flags);
}
