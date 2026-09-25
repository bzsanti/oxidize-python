"""Verify a built wheel with/without MCP extras in fresh environments.

Usage: python scripts/check_mcp_install.py WHEEL [--constraints FILE]
Network access is required for pip dependencies. Temporary environments are removed.
"""

import argparse
import os
from pathlib import Path
import subprocess
import tempfile
import venv

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tests/mcp_tests/clients/stdio_probe.py"


def run(args, cwd, env=None):
    subprocess.run([str(arg) for arg in args], cwd=cwd, env=env, check=True, timeout=300)


def create_env(root, name):
    path = root / name
    venv.EnvBuilder(with_pip=True).create(path)
    return path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--constraints", type=Path)
    parser.add_argument("--integrations-dir", type=Path, help="Also verify the sibling launcher and registry command (Unix)")
    args = parser.parse_args()
    wheel = args.wheel.resolve()
    with tempfile.TemporaryDirectory(prefix="oxidize-mcp-install-") as folder:
        root = Path(folder)
        env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
        base = create_env(root, "base")
        run([base, "-m", "pip", "install", wheel], root, env)
        run([base, "-c", '''
from importlib.util import find_spec
from oxidize_pdf import Document, Page, Font, PdfReader
assert all(find_spec(name) is None for name in ["fastmcp", "mcp", "mcp_types"])
doc = Document()
page = Page.a4()
page.set_font(Font.HELVETICA, 12)
page.text_at(50, 700, "Base package works")
doc.add_page(page)
doc.save("base.pdf")
assert "Base package works" in "\\n".join(PdfReader.open("base.pdf").extract_text())
'''], root, env)
        server = create_env(root, "server")
        install = [server, "-m", "pip", "install", str(wheel) + "[mcp]"]
        if args.constraints:
            install += ["-c", args.constraints.resolve()]
        run(install, root, env)
        run([server, "-m", "pip", "check"], root, env)
        run([server, "-c", 'from importlib.metadata import version; assert version("mcp").split(".")[0] == "2"; print({n: version(n) for n in ["oxidize-pdf", "fastmcp", "mcp", "mcp-types"]})'], root, env)
        workspace = root / "workspace"
        workspace.mkdir()
        for launch in ["module", "entrypoint"]:
            run([server, PROBE, server, launch, workspace], root, env)
        legacy = create_env(root, "legacy")
        run([legacy, "-m", "pip", "install", "mcp==1.26.0"], root, env)
        run([legacy, PROBE, server, "entrypoint", workspace], root, env)
        if args.integrations_dir:
            integrations = args.integrations_dir.resolve()
            plugin_env = {
                **env,
                "PATH": str(base.parent) + os.pathsep + env.get("PATH", ""),
                "OXIDIZE_PLUGIN_DATA": str(root / "plugin"),
                "OXIDIZE_SKIP_UPGRADE": "0",
                "PIP_FIND_LINKS": str(wheel.parent),
                "UV_FIND_LINKS": str(wheel.parent),
                "UV_CACHE_DIR": str(root / "uv-cache"),
                "OXIDIZE_TEST_LAUNCHER": str(integrations / "claude-code/bin/launch-mcp"),
                "OXIDIZE_TEST_MANIFEST": str(integrations / "mcp/server.json"),
            }
            if args.constraints:
                plugin_env["PIP_CONSTRAINT"] = str(args.constraints.resolve())
            run(["bash", plugin_env["OXIDIZE_TEST_LAUNCHER"], "check"], root, plugin_env)
            run([server, PROBE, server, "launcher", workspace], root, plugin_env)
            run([server, PROBE, server, "registry", workspace], root, plugin_env)
            # Upgrade an actual supported legacy installation, not only a fake pip.
            old_plugin = root / "legacy-plugin"
            old_python = create_env(old_plugin, "venv")
            run([old_python, "-m", "pip", "install", "oxidize-pdf[mcp]==0.19.0",
                 "fastmcp==3.1.1", "mcp==1.26.0"], root, env)
            plugin_env["OXIDIZE_PLUGIN_DATA"] = str(old_plugin)
            run(["bash", plugin_env["OXIDIZE_TEST_LAUNCHER"], "check"], root, plugin_env)
            run([server, PROBE, server, "launcher", workspace], root, plugin_env)
        print("PASS: base wheel, MCP extra, SDK v2 and isolated SDK v1 stdio")


if __name__ == "__main__":
    main()
