# PyFileSystem – File System Management and Simulation Tool

**Course area:** Operating Systems  
**Language:** Python 3  
**GUI:** Tkinter  
**Real OS integration:** Ubuntu on WSL2 (optional for simulation-only use)

## 1. Project overview

PyFileSystem is an educational desktop application demonstrating the file-system interface and implementation concepts. It has two strictly separate subsystems:

1. **Actual Linux File System:** performs real file operations only under `~/pyfilesystem_lab/lab_test` in Ubuntu WSL2.
2. **Virtual File System:** an in-memory/JSON-backed simulation of allocation, directory metadata, access methods, permissions and free-space management. It does not manipulate host files.

## 2. Features

- Create, read, append, rename, list and delete real Linux files within the lab directory.
- Inspect Linux metadata and permission modes.
- Virtual contiguous, linked and indexed allocation.
- Bitmap free-space management and block reclamation.
- Virtual directory tree.
- Sequential and direct record access in the simulator.
- Simulated owner/group/others permission checks.
- JSON persistence and consistency validation.
- Tkinter desktop interface.

## 3. Windows setup

Install Python 3.11 or later. Open PowerShell in the project folder:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

The simulator and GUI work without WSL. The Actual Linux File System page requires Ubuntu WSL2.

## 4. Optional Ubuntu WSL2 setup

WSL2 installs an Ubuntu environment alongside Windows; it does not replace Windows or create a dual-boot system.

In PowerShell as Administrator:

```powershell
wsl --install -d Ubuntu
```

Restart if requested, launch Ubuntu, and create the Linux username/password. Then run inside Ubuntu:

```bash
mkdir -p ~/pyfilesystem_lab/lab_test
chmod 700 ~/pyfilesystem_lab
chmod 700 ~/pyfilesystem_lab/lab_test
```

Copy this project folder into Ubuntu's home directory (or otherwise make the Python package available to the WSL interpreter). One convenient approach from Ubuntu, if the project is at `C:\PyFileSystem`, is:

```bash
cp -r /mnt/c/PyFileSystem ~/PyFileSystem
cd ~/PyFileSystem
python3 -m pyfilesystem.linux_worker
```

The Windows GUI invokes `python3 -m pyfilesystem.linux_worker` inside the configured Ubuntu distribution. Ensure the package is present in Ubuntu's current working directory; see the bridge note below.

## 5. Important WSL bridge note

The bridge runs a fixed Python module command in the WSL default working directory. For reliable use, keep a copy of the project at `~/PyFileSystem` inside Ubuntu and modify `wsl_bridge.py` to add `--cd ~/PyFileSystem` before the Python command if your WSL version supports it, or use a fixed `bash -lc 'cd "$HOME/PyFileSystem" && exec python3 -m pyfilesystem.linux_worker'` invocation with strict constant command text. Do not interpolate user-supplied path or shell text into that command. The supplied bridge intentionally avoids shell execution; if the module is not on WSL's Python path, the real subsystem will report a worker error while simulation remains usable.

## 6. Run tests

```powershell
python -m pip install pytest
python -m pytest -q
```

## 7. Safety model

- The real worker's root is fixed to `~/pyfilesystem_lab/lab_test`.
- Real operation paths are relative only.
- Parent traversal and symbolic links are rejected.
- Files are created with mode `600`; directories with mode `700`.
- Supported permission changes are restricted to `600`, `640`, `700`, and `750`.
- No `sudo`, recursive deletion, or `chmod 777`.
- The GUI never falls back to Windows file operations if WSL is unavailable.
- The simulator does not access real files.

**Review the code and run the tests in your own environment before submission.** The project is a starter implementation for an academic demonstration; verify WSL integration and all required evidence on the target PC.
