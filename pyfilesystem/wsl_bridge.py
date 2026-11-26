"""Windows-to-WSL JSON bridge. Simulation remains available without WSL."""
import json, subprocess, shutil, os, sys

class WSLBridge:
    def __init__(self, distro="Ubuntu", timeout=12):
        self.distro, self.timeout = distro, timeout

    def available(self):
        if not shutil.which("wsl.exe"): return False
        try:
            p = subprocess.run(["wsl.exe", "-l", "-q"], capture_output=True, text=True, timeout=self.timeout)
            output = (p.stdout + p.stderr).replace("\x00", "")
            return p.returncode == 0 and self.distro.lower() in output.lower()
        except Exception:
            return False

    def request(self, payload):
        if not self.available(): raise RuntimeError("Ubuntu WSL distribution is unavailable. Install/start WSL to enable real Linux operations.")
        # Fixed module command; user data travels only through stdin JSON.
        proc = subprocess.run(
            ["wsl.exe", "-d", self.distro, "--cd", "~/PyFileSystem", "--", "python3", "-m", "pyfilesystem.linux_worker"],
            input=json.dumps(payload) + "\n", capture_output=True, text=True, timeout=self.timeout
        )
        if proc.returncode != 0: raise RuntimeError(proc.stderr.strip() or "Linux worker failed.")
        try: response = json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception: raise RuntimeError("Invalid response from Linux worker: " + proc.stdout[:300])
        if not response.get("ok"): raise RuntimeError(response.get("error", "Linux operation failed."))
        return response["result"]
