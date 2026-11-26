"""A purely virtual file system. This module never performs host file operations."""
from dataclasses import dataclass, asdict
from math import ceil
from pathlib import PurePosixPath
from datetime import datetime, timezone
import json
from .validators import validate_name, validate_size, validate_record_position

@dataclass
class VirtualFile:
    name: str
    path: str
    size_kb: int
    method: str
    blocks: list
    records: list
    permissions: str = "640"
    created: str = ""
    modified: str = ""

class VirtualDisk:
    def __init__(self, capacity_kb=100, block_size_kb=1):
        if capacity_kb <= 0 or block_size_kb <= 0 or capacity_kb % block_size_kb:
            raise ValueError("Capacity and block size must be positive, and capacity must be divisible by block size.")
        self.capacity_kb = capacity_kb
        self.block_size_kb = block_size_kb
        self.total_blocks = capacity_kb // block_size_kb
        self.bitmap = [0] * self.total_blocks
        self.files = {}
        self.directories = {"/": []}
        self.activity = []

    @property
    def free_blocks(self): return self.bitmap.count(0)
    @property
    def used_blocks(self): return self.bitmap.count(1)
    @property
    def free_kb(self): return self.free_blocks * self.block_size_kb
    @property
    def used_kb(self): return self.used_blocks * self.block_size_kb

    def _log(self, message):
        self.activity.insert(0, f"{datetime.now().astimezone().isoformat(timespec='seconds')}  {message}")
        self.activity = self.activity[:100]

    def _path(self, path):
        p = PurePosixPath(path or "/")
        if not p.is_absolute(): p = PurePosixPath("/") / p
        if ".." in p.parts: raise ValueError("Parent traversal is not allowed.")
        normalized = str(p)
        if normalized not in self.directories: raise ValueError("Directory does not exist.")
        return normalized

    def mkdir(self, name, parent="/"):
        name = validate_name(name); parent = self._path(parent)
        path = str(PurePosixPath(parent) / name)
        if path in self.directories or path in self.files: raise FileExistsError("Name already exists.")
        self.directories[path] = []
        self.directories[parent].append({"name": name, "type": "directory", "path": path})
        self._log(f"Created directory {path}")
        return path

    def _free(self, count):
        return [i for i, v in enumerate(self.bitmap) if v == 0][:count]

    def create_file(self, name, size_kb, method="contiguous", directory="/", content=""):
        name = validate_name(name); size_kb = validate_size(size_kb, self.capacity_kb)
        directory = self._path(directory)
        path = str(PurePosixPath(directory) / name)
        if path in self.files or path in self.directories: raise FileExistsError("Name already exists.")
        needed = max(1, ceil(size_kb / self.block_size_kb))
        if needed > self.free_blocks: raise OSError("Insufficient virtual disk space.")
        if method not in {"contiguous", "linked", "indexed"}: raise ValueError("Unknown allocation method.")
        if method == "contiguous":
            blocks = None
            for start in range(self.total_blocks-needed+1):
                candidate = list(range(start, start+needed))
                if all(self.bitmap[i] == 0 for i in candidate):
                    blocks = candidate; break
            if blocks is None: raise OSError("Enough free blocks may exist, but no contiguous run is available.")
        elif method == "linked":
            blocks = self._free(needed)
        else:
            # Reserve one index block plus data blocks.
            if needed + 1 > self.free_blocks: raise OSError("Indexed allocation needs an index block plus data blocks.")
            blocks = self._free(needed+1)
        for b in blocks: self.bitmap[b] = 1
        now = datetime.now(timezone.utc).isoformat()
        records = content.splitlines() if content else []
        vf = VirtualFile(name, path, size_kb, method, blocks, records, "640", now, now)
        self.files[path] = vf
        self.directories[directory].append({"name": name, "type": "file", "path": path})
        self._log(f"Created {path} using {method} allocation ({len(blocks)} blocks)")
        return vf

    def delete_file(self, path):
        if path not in self.files: raise FileNotFoundError(path)
        vf = self.files.pop(path)
        for b in vf.blocks: self.bitmap[b] = 0
        parent = str(PurePosixPath(path).parent)
        self.directories[parent] = [x for x in self.directories[parent] if x["path"] != path]
        self._log(f"Deleted {path}; reclaimed {len(vf.blocks)} blocks")
        return len(vf.blocks)

    def rename_file(self, path, new_name):
        if path not in self.files: raise FileNotFoundError(path)
        new_name = validate_name(new_name)
        parent = str(PurePosixPath(path).parent); new_path = str(PurePosixPath(parent)/new_name)
        if new_path in self.files or new_path in self.directories: raise FileExistsError(new_path)
        vf = self.files.pop(path); vf.name = new_name; vf.path = new_path
        vf.modified = datetime.now(timezone.utc).isoformat()
        self.files[new_path] = vf
        for item in self.directories[parent]:
            if item["path"] == path: item.update(name=new_name, path=new_path)
        self._log(f"Renamed {path} to {new_path}")
        return vf

    def set_permissions(self, path, octal):
        if path not in self.files: raise FileNotFoundError(path)
        s = str(octal)
        if len(s) != 3 or any(c not in "01234567" for c in s): raise ValueError("Permissions must be three octal digits.")
        self.files[path].permissions = s
        self._log(f"Changed simulated permissions for {path} to {s}")

    def check_access(self, path, role, operation):
        if path not in self.files: raise FileNotFoundError(path)
        if role not in {"owner", "group", "others"}: raise ValueError("Unknown role.")
        bit = {"read": 4, "write": 2, "execute": 1}.get(operation)
        if bit is None: raise ValueError("Unknown operation.")
        index = {"owner": 0, "group": 1, "others": 2}[role]
        allowed = (int(self.files[path].permissions[index]) & bit) != 0
        self._log(f"Access check {role}/{operation} on {path}: {'ALLOW' if allowed else 'DENY'}")
        return allowed

    def sequential_records(self, path):
        if path not in self.files: raise FileNotFoundError(path)
        return list(self.files[path].records)

    def direct_record(self, path, position):
        records = self.sequential_records(path)
        return records[validate_record_position(position, len(records))]

    def update_record(self, path, position, value):
        records = self.sequential_records(path)
        pos = validate_record_position(position, len(records))
        records[pos] = str(value)
        self.files[path].modified = datetime.now(timezone.utc).isoformat()
        self._log(f"Updated record {pos} in {path}")

    def tree(self):
        return {p: list(items) for p, items in self.directories.items()}

    def to_dict(self):
        return {"capacity_kb": self.capacity_kb, "block_size_kb": self.block_size_kb,
                "bitmap": self.bitmap, "files": {p: asdict(f) for p, f in self.files.items()},
                "directories": self.directories, "activity": self.activity}

    @classmethod
    def from_dict(cls, d):
        disk = cls(int(d["capacity_kb"]), int(d["block_size_kb"]))
        bitmap = d["bitmap"]
        if len(bitmap) != disk.total_blocks or any(x not in (0,1) for x in bitmap):
            raise ValueError("Invalid bitmap in saved simulation.")
        disk.bitmap = list(bitmap)
        disk.files = {p: VirtualFile(**v) for p,v in d["files"].items()}
        disk.directories = d["directories"]
        disk.activity = d.get("activity", [])
        # Verify every allocated block agrees with bitmap.
        referenced = []
        for f in disk.files.values(): referenced.extend(f.blocks)
        if len(referenced) != len(set(referenced)) or any(b < 0 or b >= disk.total_blocks for b in referenced):
            raise ValueError("Corrupt allocation map.")
        expected = [0] * disk.total_blocks
        for b in referenced: expected[b] = 1
        if expected != disk.bitmap: raise ValueError("Bitmap and file allocations do not match.")
        return disk

def save_disk(disk, path):
    import os
    from pathlib import Path
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(disk.to_dict(), indent=2), encoding="utf-8")
    os.replace(tmp, target)

def load_disk(path):
    from pathlib import Path
    p = Path(path)
    return VirtualDisk.from_dict(json.loads(p.read_text(encoding="utf-8"))) if p.exists() else VirtualDisk()
