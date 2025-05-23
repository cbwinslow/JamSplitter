"""
test_cli_integration.py ─────────────────────────────────────────────────────
Author : ChatGPT for CBW  ✦ 2025-05-23
Summary: Integration test for main.py CLI
ModLog : 2025-05-23  Initial version
"""
import subprocess, sys, os, tempfile, shutil
def test_cli_exit(tmp_path):
    # Prepare project copy
    proj = tmp_path / "proj"
    shutil.copytree(os.getcwd(), proj)
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "fake"
    # Run and send exit
    p = subprocess.Popen([sys.executable, "main.py"], cwd=proj,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out, err = p.communicate(b"exit
", timeout=10)
    assert b"Goodbye!" in out
