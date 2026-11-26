import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from pathlib import Path
from .simulator import VirtualDisk, save_disk, load_disk
from .config import DATA_FILE
from .wsl_bridge import WSLBridge

BG="#101827"; PANEL="#182538"; ACCENT="#3B82F6"; TEXT="#E8EEF7"; MUTED="#9BAAC0"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyFileSystem | File System Management & Simulation")
        self.geometry("1180x760"); self.minsize(950,620); self.configure(bg=BG)
        try: self.disk=load_disk(DATA_FILE)
        except Exception as e:
            messagebox.showwarning("Simulation reset", f"Saved simulation was invalid and a fresh disk was loaded.\n{e}")
            self.disk=VirtualDisk()
        self.bridge=WSLBridge()
        self._style()
        self._layout()
        self.show_dashboard()

    def _style(self):
        style=ttk.Style(self); style.theme_use("clam")
        style.configure("Treeview", background=PANEL, foreground=TEXT, fieldbackground=PANEL, rowheight=28)
        style.configure("Treeview.Heading", background="#263A55", foreground=TEXT)
        style.map("Treeview", background=[("selected",ACCENT)])
        style.configure("TCombobox", fieldbackground=PANEL, background=PANEL, foreground=TEXT)

    def _layout(self):
        header=tk.Frame(self,bg="#0B1320",height=62); header.pack(fill="x")
        tk.Label(header,text="◈  PyFileSystem",bg="#0B1320",fg=TEXT,font=("Segoe UI",18,"bold")).pack(side="left",padx=22,pady=14)
        self.status=tk.Label(header,text="Checking Ubuntu WSL…",bg="#0B1320",fg=MUTED,font=("Segoe UI",10)); self.status.pack(side="right",padx=20)
        body=tk.Frame(self,bg=BG); body.pack(fill="both",expand=True)
        nav=tk.Frame(body,bg="#121E2E",width=220); nav.pack(side="left",fill="y"); nav.pack_propagate(False)
        tk.Label(nav,text="WORKSPACE",bg="#121E2E",fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w",padx=18,pady=(22,8))
        for label,fn in [("Dashboard",self.show_dashboard),("Actual Linux Files",self.show_actual),
                         ("Virtual File Manager",self.show_files),("Allocation Simulator",self.show_allocation),
                         ("Free-space Bitmap",self.show_bitmap),("Access & Permissions",self.show_permissions),
                         ("Directory Tree",self.show_tree),("About",self.show_about)]:
            tk.Button(nav,text="  "+label,command=fn,anchor="w",bg="#121E2E",fg=TEXT,activebackground="#263A55",
                      activeforeground="white",relief="flat",font=("Segoe UI",10),padx=12,pady=10).pack(fill="x",padx=8,pady=2)
        self.content=tk.Frame(body,bg=BG); self.content.pack(side="left",fill="both",expand=True,padx=24,pady=22)
        self.protocol("WM_DELETE_WINDOW",self.on_close)
        self.after(100, self.check_wsl)

    def clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def title_block(self,title,sub):
        tk.Label(self.content,text=title,bg=BG,fg=TEXT,font=("Segoe UI",23,"bold")).pack(anchor="w")
        tk.Label(self.content,text=sub,bg=BG,fg=MUTED,font=("Segoe UI",10)).pack(anchor="w",pady=(3,18))

    def card(self,parent,label,value):
        f=tk.Frame(parent,bg=PANEL,padx=18,pady=16); f.pack(side="left",fill="both",expand=True,padx=(0,12))
        tk.Label(f,text=label,bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w")
        tk.Label(f,text=str(value),bg=PANEL,fg=TEXT,font=("Segoe UI",22,"bold")).pack(anchor="w",pady=(6,0))
        return f

    def check_wsl(self):
        ok=self.bridge.available()
        self.status.config(text=("● Ubuntu WSL connected" if ok else "○ WSL unavailable — simulation mode"),
                           fg=("#4ADE80" if ok else "#FBBF24"))

    def save(self):
        save_disk(self.disk,DATA_FILE)

    def show_dashboard(self):
        self.clear(); self.title_block("Dashboard","Overview of the virtual disk and the isolated Linux laboratory.")
        row=tk.Frame(self.content,bg=BG); row.pack(fill="x",pady=6)
        self.card(row,"Virtual capacity",f"{self.disk.capacity_kb} KB")
        self.card(row,"Used virtual space",f"{self.disk.used_kb} KB")
        self.card(row,"Free virtual space",f"{self.disk.free_kb} KB")
        self.card(row,"Virtual files",len(self.disk.files))
        box=tk.Frame(self.content,bg=PANEL,padx=20,pady=18); box.pack(fill="x",pady=16)
        tk.Label(box,text="Storage utilization",bg=PANEL,fg=TEXT,font=("Segoe UI",13,"bold")).pack(anchor="w")
        pct=(self.disk.used_blocks/self.disk.total_blocks)*100
        tk.Label(box,text=f"{pct:.1f}% occupied  |  {self.disk.used_blocks} used blocks  |  {self.disk.free_blocks} free blocks",
                 bg=PANEL,fg=MUTED,font=("Segoe UI",10)).pack(anchor="w",pady=8)
        cv=tk.Canvas(box,height=22,bg="#263A55",highlightthickness=0); cv.pack(fill="x")
        cv.create_rectangle(0,0,max(1,cv.winfo_width()*pct/100),22,fill=ACCENT,outline="")
        cv.bind("<Configure>",lambda e:(cv.delete("all"),cv.create_rectangle(0,0,e.width*pct/100,22,fill=ACCENT,outline="")))
        note=tk.Frame(self.content,bg=PANEL,padx=20,pady=16); note.pack(fill="x")
        tk.Label(note,text="Safety boundary",bg=PANEL,fg=TEXT,font=("Segoe UI",12,"bold")).pack(anchor="w")
        tk.Label(note,text="REAL operations: Ubuntu WSL only, under ~/pyfilesystem_lab/lab_test.\nSIMULATION: virtual disk stored separately in data/simulation.json. The two systems do not share files or blocks.",
                 bg=PANEL,fg=MUTED,justify="left",font=("Segoe UI",10)).pack(anchor="w",pady=8)

    def show_actual(self):
        self.clear(); self.title_block("Actual Linux File System","Genuine Linux operations. All paths are relative to the approved lab_test directory.")
        tk.Label(self.content,text="Relative path (e.g. notes.txt or experiments/notes.txt)",bg=BG,fg=MUTED).pack(anchor="w")
        name=tk.Entry(self.content,bg=PANEL,fg=TEXT,insertbackground=TEXT,relief="flat"); name.pack(fill="x",pady=6,ipady=8)
        tk.Label(self.content,text="Content / append text",bg=BG,fg=MUTED).pack(anchor="w",pady=(8,0))
        content=tk.Text(self.content,height=7,bg=PANEL,fg=TEXT,insertbackground=TEXT,relief="flat"); content.pack(fill="x",pady=6)
        output=tk.Text(self.content,height=12,bg="#0B1320",fg="#C8D5E5",relief="flat"); output.pack(fill="both",expand=True,pady=8)
        def run(op,extra=None):
            try:
                payload={"op":op,"name":name.get().strip()}
                if extra: payload.update(extra)
                if op in ("create","append"): payload["content"]=content.get("1.0","end-1c")
                result=self.bridge.request(payload)
                output.insert("end",json_pretty(result)+"\n")
            except Exception as e: messagebox.showerror("Linux operation rejected",str(e))
        buttons=tk.Frame(self.content,bg=BG); buttons.pack(fill="x")
        for label,op in [("Create","create"),("Read","read"),("Append","append"),("Delete","delete"),("Metadata","stat"),("List parent","list")]:
            tk.Button(buttons,text=label,command=lambda o=op:run(o),bg="#263A55",fg=TEXT,relief="flat",padx=12,pady=7).pack(side="left",padx=3)
        tk.Button(buttons,text="Create directory",command=lambda:run("mkdir"),bg=ACCENT,fg="white",relief="flat",padx=10,pady=7).pack(side="left",padx=3)
        tk.Button(buttons,text="chmod 640",command=lambda:run("chmod",{"mode":"640"}),bg="#36516F",fg="white",relief="flat",padx=10,pady=7).pack(side="left",padx=3)
        tk.Button(buttons,text="Rename",command=lambda:self.rename_linux(name,run),bg="#36516F",fg="white",relief="flat",padx=10,pady=7).pack(side="left",padx=3)
        tk.Label(self.content,text="If Ubuntu is not installed, this section remains unavailable; all simulation modules still work.",bg=BG,fg="#FBBF24").pack(anchor="w",pady=8)

    def rename_linux(self,name,run):
        new=simpledialog.askstring("Rename","New filename:")
        if new: 
            try: self.output_unused = self.bridge.request({"op":"rename","name":name.get().strip(),"new_name":new})
            except Exception as e: messagebox.showerror("Rename failed",str(e))

    def show_files(self):
        self.clear(); self.title_block("Virtual File Manager","Create virtual files and directories. No real operating-system files are touched.")
        bar=tk.Frame(self.content,bg=BG); bar.pack(fill="x")
        name=tk.Entry(bar,width=22); name.insert(0,"example.txt"); name.pack(side="left",ipady=6,padx=3)
        size=tk.Entry(bar,width=8); size.insert(0,"2"); size.pack(side="left",ipady=6,padx=3)
        method=ttk.Combobox(bar,values=["contiguous","linked","indexed"],width=13,state="readonly"); method.set("contiguous"); method.pack(side="left",padx=3)
        def create():
            try:
                self.disk.create_file(name.get(),int(size.get()),method.get(),content="First record\nSecond record\nThird record")
                self.save(); self.show_files()
            except Exception as e: messagebox.showerror("Create failed",str(e))
        tk.Button(bar,text="＋ Create virtual file",command=create,bg=ACCENT,fg="white",relief="flat",padx=12,pady=7).pack(side="left",padx=6)
        tree=ttk.Treeview(self.content,columns=("size","method","blocks","perm"),show="headings")
        for c,w in [("size",100),("method",150),("blocks",200),("perm",90)]:
            tree.heading(c,text=c.title()); tree.column(c,width=w)
        tree.pack(fill="both",expand=True,pady=14)
        for p,f in self.disk.files.items(): tree.insert("", "end",iid=p,values=(f.size_kb+" KB" if isinstance(f.size_kb,str) else f"{f.size_kb} KB",f.method,str(f.blocks),f.permissions),text=p)
        def delete():
            sel=tree.selection()
            if not sel: return
            if messagebox.askyesno("Confirm deletion","Delete selected virtual file and reclaim its blocks?"):
                self.disk.delete_file(sel[0]); self.save(); self.show_files()
        tk.Button(self.content,text="Delete selected virtual file",command=delete,bg="#9B3C4B",fg="white",relief="flat",padx=12,pady=8).pack(anchor="e")

    def show_allocation(self):
        self.clear(); self.title_block("Allocation Simulator","Compare contiguous, linked and indexed allocation on the virtual disk.")
        tk.Label(self.content,text="Allocation methods reserve different virtual block layouts. Indexed allocation uses an extra index block.",bg=BG,fg=MUTED).pack(anchor="w",pady=6)
        self.show_bitmap_body()

    def show_bitmap_body(self):
        grid=tk.Frame(self.content,bg=BG); grid.pack(fill="both",expand=True,pady=12)
        for i,v in enumerate(self.disk.bitmap):
            cell=tk.Frame(grid,bg=("#267B52" if v else "#34445A"),width=66,height=48)
            cell.grid(row=i//10,column=i%10,padx=3,pady=3,sticky="nsew")
            cell.pack_propagate(False)
            tk.Label(cell,text=str(i),bg=cell["bg"],fg="white",font=("Segoe UI",9,"bold")).pack(expand=True)
        for c in range(10): grid.grid_columnconfigure(c,weight=1)
        tk.Label(self.content,text=f"Green = occupied     Slate = free     |     {self.disk.used_blocks}/{self.disk.total_blocks} occupied blocks",
                 bg=BG,fg=MUTED).pack(anchor="w")

    def show_bitmap(self):
        self.clear(); self.title_block("Free-space Bitmap","Bitmap convention: 0 = free block; 1 = occupied block.")
        self.show_bitmap_body()

    def show_permissions(self):
        self.clear(); self.title_block("Access & Permissions","Simulated owner/group/others permission checks.")
        paths=list(self.disk.files)
        if not paths:
            tk.Label(self.content,text="Create a virtual file first in Virtual File Manager.",bg=BG,fg=MUTED).pack(anchor="w"); return
        selected=tk.StringVar(value=paths[0])
        ttk.Combobox(self.content,textvariable=selected,values=paths,state="readonly",width=55).pack(anchor="w",pady=6)
        role=ttk.Combobox(self.content,values=["owner","group","others"],state="readonly"); role.set("owner"); role.pack(anchor="w",pady=6)
        op=ttk.Combobox(self.content,values=["read","write","execute"],state="readonly"); op.set("read"); op.pack(anchor="w",pady=6)
        result=tk.Label(self.content,text="Choose a role and operation.",bg=BG,fg=TEXT,font=("Segoe UI",14)); result.pack(anchor="w",pady=18)
        def check():
            try:
                allowed=self.disk.check_access(selected.get(),role.get(),op.get()); self.save()
                result.config(text=("ACCESS ALLOWED" if allowed else "ACCESS DENIED"),fg=("#4ADE80" if allowed else "#F87171"))
            except Exception as e: messagebox.showerror("Check failed",str(e))
        tk.Button(self.content,text="Check access",command=check,bg=ACCENT,fg="white",relief="flat",padx=14,pady=8).pack(anchor="w")
        tk.Label(self.content,text="Default simulated permission: 640 (owner rw-, group r--, others ---).",bg=BG,fg=MUTED).pack(anchor="w",pady=12)

    def show_tree(self):
        self.clear(); self.title_block("Directory Organization","Current virtual directory tree.")
        tree=ttk.Treeview(self.content); tree.pack(fill="both",expand=True)
        root=tree.insert("","end",text="/",open=True)
        for path,items in self.disk.directories.items():
            if path=="/": parent=root
            else:
                parent=root
                for part in Path(path).parts:
                    if part=="/": continue
                    found=None
                    for child in tree.get_children(parent):
                        if tree.item(child,"text")==part: found=child; break
                    if found is None: found=tree.insert(parent,"end",text=part,open=True)
                    parent=found
            for item in items: tree.insert(parent,"end",text=item["name"]+("/" if item["type"]=="directory" else ""))
        bar=tk.Frame(self.content,bg=BG); bar.pack(fill="x",pady=8)
        n=tk.Entry(bar); n.insert(0,"documents"); n.pack(side="left",ipady=6)
        def mkdir():
            try: self.disk.mkdir(n.get()); self.save(); self.show_tree()
            except Exception as e: messagebox.showerror("Directory error",str(e))
        tk.Button(bar,text="Create directory",command=mkdir,bg=ACCENT,fg="white",relief="flat",padx=10,pady=7).pack(side="left",padx=6)

    def show_about(self):
        self.clear(); self.title_block("About PyFileSystem","Operating Systems academic project")
        text=("PyFileSystem demonstrates the file-system interface and implementation concepts: file operations, "
              "directory structures, sequential/direct access, contiguous/linked/indexed allocation, bitmap free-space "
              "management, deletion and permissions.\n\n"
              "The Actual Linux subsystem is isolated in Ubuntu WSL and confines operations to "
              "~/pyfilesystem_lab/lab_test. The virtual disk is an independent Python simulation persisted as JSON.\n\n"
              "Educational note: the simulation models allocation metadata; it does not format or mount a real disk.")
        tk.Label(self.content,text=text,bg=PANEL,fg=TEXT,justify="left",wraplength=800,padx=22,pady=22,font=("Segoe UI",11)).pack(fill="x")

    def on_close(self):
        try: self.save()
        except Exception: pass
        self.destroy()

def json_pretty(obj):
    import json
    return json.dumps(obj,indent=2,ensure_ascii=False)

def main():
    App().mainloop()
