"""Run synthetic core-event conversion tests with an embedded CPython on Linux.

The extension-module feature intentionally omits libpython linkage for wheels.
Only this test executable links the active Python library; production build
features and dependency policy remain unchanged.
"""
import json
import os
from pathlib import Path
import subprocess
import shlex
import sys
import sysconfig


def main() -> None:
    if sys.platform != 'linux':
        raise SystemExit('Run native event tests on Linux with a shared CPython library')
    library = sysconfig.get_config_var('INSTSONAME') or sysconfig.get_config_var('LDLIBRARY')
    libdir = sysconfig.get_config_var('LIBDIR')
    if not library or not libdir or not (Path(libdir) / library).is_file():
        raise SystemExit('Shared CPython library not found')
    env = os.environ.copy()
    env['PYO3_PYTHON'] = sys.executable
    flags = (env['CARGO_ENCODED_RUSTFLAGS'].split('\x1f')
             if 'CARGO_ENCODED_RUSTFLAGS' in env else shlex.split(env.get('RUSTFLAGS', '')))
    flags += ['-C', f'link-arg={Path(libdir) / library}']
    env['CARGO_ENCODED_RUSTFLAGS'] = '\x1f'.join(flags)
    env['CARGO_TARGET_DIR'] = str(Path('target/native-event-tests').resolve())
    result = subprocess.run([
        'cargo', 'test', '--locked', '--offline', '--lib', '--no-run',
        '--message-format=json',
    ], env=env, text=True, stdout=subprocess.PIPE)
    executables = []
    for line in result.stdout.splitlines():
        event = json.loads(line)
        if event.get('reason') == 'compiler-message':
            print(event['message'].get('rendered', ''), end='')
        if event.get('reason') == 'compiler-artifact' and event.get('executable'):
            executables.append(event['executable'])
    result.check_returncode()
    if len(executables) != 1:
        raise SystemExit(f'Expected one test executable, found {executables}')
    env['LD_LIBRARY_PATH'] = libdir + os.pathsep + env.get('LD_LIBRARY_PATH', '')
    listing = subprocess.check_output([executables[0], 'parse_events::tests', '--list'], env=env, text=True)
    for name in ('preserves_nonempty_xref_and_large_offsets',
                 'preserves_trailer_and_nonplaceholder_object',
                 'preserves_binary_stream_bytes_without_decoding'):
        if f'parse_events::tests::{name}: test' not in listing:
            raise SystemExit(f'Required native contract test missing: {name}')
    subprocess.run([executables[0], 'parse_events::tests', '--nocapture'], env=env, check=True)


if __name__ == '__main__':
    main()
