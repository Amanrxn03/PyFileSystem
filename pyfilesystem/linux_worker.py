"""Linux-only worker. Every real operation is confined to ~/pyfilesystem_lab/lab_test."""
import json, os, sys, shutil, stat
from pathlib import Path

ROOT = (Path.home() / "pyfilesystem_lab" / "lab_test").resolve()
ALLOWED_MODES = {"600", "640", "700", "750"}

def ensure_root():
    ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(ROOT.parent, 0o700)
    os.chmod(ROOT, 0o700)

def safe_target(name):
    if not isinstance(name, str) or not name or "\x00" in name:
        raise ValueError("Invalid path.")
    rel = Path(name)
    if rel.is_absolute() or any(part in ("..", ".") for part in rel.parts):
        raise ValueError("Only relative paths inside lab_test are accepted.")
    target = ROOT.joinpath(rel)
    # Reject symlinks in every existing path component, including final target.
    current = ROOT
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symbolic links are not permitted.")
    resolved_parent = target.parent.resolve()
    if resolved_parent != ROOT and ROOT not in resolved_parent.parents:
        raise ValueError("Path escapes laboratory directory.")
    if target.exists() and target.resolve() != ROOT and ROOT not in target.resolve().parents:
        raise ValueError("Path escapes laboratory directory.")
    return target

def handle(req):
    ensure_root()
    op = req.get("op")
    if op == "status":
        return {"root": str(ROOT), "exists": ROOT.is_dir(), "free_bytes": shutil.disk_usage(ROOT).free}
    name = req.get("name", "")
    target = safe_target(name)
    if op == "list":
        directory = target if target.is_dir() else target.parent
        return {"items": [{"name": p.name, "type": "directory" if p.is_dir() else "file",
                           "size": p.stat().st_size, "mode": oct(stat.S_IMODE(p.stat().st_mode))}
                          for p in sorted(directory.iterdir())]}
    if op == "mkdir":
        target.mkdir(mode=0o700, parents=False, exist_ok=False); os.chmod(target, 0o700)
        return {"message": "Directory created", "path": str(target)}
    if op == "create":
        if len(name) > 128 or target.name in ("", ".", ".."): raise ValueError("Invalid filename.")
        if target.exists(): raise FileExistsError("Target already exists.")
        content = req.get("content", "")
        if not isinstance(content, str) or len(content.encode("utf-8")) > 1024*1024:
            raise ValueError("Content exceeds 1 MiB limit.")
        if shutil.disk_usage(target.parent).free < len(content.encode("utf-8")) + 4096:
            raise OSError("Insufficient available disk space.")
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f: f.write(content)
        os.chmod(target, 0o600)
        return {"message": "File created", "path": str(target)}
    if op == "read":
        if not target.is_file(): raise FileNotFoundError(name)
        return {"content": target.read_text(encoding="utf-8")}
    if op == "append":
        content = req.get("content", "")
        if not target.is_file(): raise FileNotFoundError(name)
        if len(content.encode("utf-8")) > 1024*1024: raise ValueError("Append exceeds 1 MiB.")
        if shutil.disk_usage(target.parent).free < len(content.encode("utf-8")) + 4096:
            raise OSError("Insufficient available disk space.")
        with target.open("a", encoding="utf-8") as f: f.write(content)
        return {"message": "Content appended"}
    if op == "rename":
        new_name = req.get("new_name", "")
        if not new_name or Path(new_name).name != new_name or new_name in (".", ".."):
            raise ValueError("New name must be a simple filename.")
        dest = safe_target(str(Path(name).parent / new_name))
        if dest.exists(): raise FileExistsError("Destination exists.")
        target.rename(dest); return {"message": "Renamed", "path": str(dest)}
    if op == "delete":
        if not target.is_file() or target.is_symlink(): raise ValueError("Only individual regular files can be deleted.")
        target.unlink(); return {"message": "File deleted"}
    if op == "chmod":
        mode = str(req.get("mode", ""))
        if mode not in ALLOWED_MODES: raise ValueError("Allowed modes: " + ", ".join(sorted(ALLOWED_MODES)))
        if not target.exists() or target.is_symlink(): raise FileNotFoundError(name)
        os.chmod(target, int(mode, 8), follow_symlinks=False)
        return {"message": "Permission changed", "mode": mode}
    if op == "stat":
        if not target.exists() or target.is_symlink(): raise FileNotFoundError(name)
        s = target.stat()
        return {"name": target.name, "size": s.st_size, "mode_octal": format(stat.S_IMODE(s.st_mode), "03o"),
                "mode_symbolic": stat.filemode(s.st_mode), "modified": s.st_mtime, "accessed": s.st_atime,
                "changed": s.st_ctime, "type": "directory" if target.is_dir() else "file"}
    raise ValueError("Unsupported operation.")

def main():
    try:
        request = json.loads(sys.stdin.readline())
        result = handle(request)
        print(json.dumps({"ok": True, "result": result}))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}))

if __name__ == "__main__":
    main()
