import customtkinter as ctk
import json
import os
from tkinter import messagebox, filedialog
from copy import deepcopy

SEED_DIR = os.path.join(os.path.dirname(__file__), "SeededData")
RARITY_OPTIONS = ["common", "uncommon", "rare", "epic", "legendary"]
RARITY_WEIGHTS = {"common": 1000, "uncommon": 400, "rare": 100, "epic": 25, "legendary": 5}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def load_json(filename: str) -> dict:
    path = os.path.join(SEED_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(filename: str, data: dict):
    os.makedirs(SEED_DIR, exist_ok=True)
    path = os.path.join(SEED_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ─── Reusable Widgets ─────────────────────────────────────────────────────────

class LabeledEntry(ctk.CTkFrame):
    def __init__(self, master, label: str, placeholder: str = "", width: int = 200, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        ctk.CTkLabel(self, text=label, font=("Consolas", 12), text_color="#888").pack(anchor="w")
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder, width=width, font=("Consolas", 13))
        self.entry.pack(fill="x")

    def get(self): return self.entry.get().strip()
    def set(self, val): self.entry.delete(0, "end"); self.entry.insert(0, str(val))
    def clear(self): self.entry.delete(0, "end")

class LabeledDropdown(ctk.CTkFrame):
    def __init__(self, master, label: str, values: list, width: int = 200, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        ctk.CTkLabel(self, text=label, font=("Consolas", 12), text_color="#888").pack(anchor="w")
        self.var = ctk.StringVar(value=values[0])
        self.menu = ctk.CTkOptionMenu(self, values=values, variable=self.var, width=width, font=("Consolas", 13))
        self.menu.pack(fill="x")

    def get(self): return self.var.get()
    def set(self, val): self.var.set(val)

# ─── Fish Editor Tab ───────────────────────────────────────────────────────────

class FishTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.fish_data: list = []
        self.selected_index: int = -1
        self._build()
        self._load()

    def _build(self):
        self.grid_columnconfigure(0, weight=1, minsize=200)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # ── Left panel: list
        left = ctk.CTkFrame(self, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="FISH", font=("Consolas", 13, "bold"), text_color="#4FC3F7").grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 4))

        self.listbox = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.listbox.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)
        self.listbox.grid_columnconfigure(0, weight=1)

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=6, pady=8)
        btn_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_row, text="+ New", command=self._new, font=("Consolas", 12),
                      height=30, fg_color="#1E3A5F", hover_color="#2A5298").grid(row=0, column=0, padx=(0,3), sticky="ew")
        ctk.CTkButton(btn_row, text="Delete", command=self._delete, font=("Consolas", 12),
                      height=30, fg_color="#4A1515", hover_color="#8B2020").grid(row=0, column=1, padx=(3,0), sticky="ew")

        # ── Right panel: form
        right = ctk.CTkFrame(self, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(right, text="FISH PROPERTIES", font=("Consolas", 13, "bold"), text_color="#4FC3F7").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 8))

        self.f_key        = LabeledEntry(right, "Key (unique id)", "common_carp")
        self.f_name       = LabeledEntry(right, "Display Name", "Common Carp")
        self.f_rarity     = LabeledDropdown(right, "Rarity", RARITY_OPTIONS)
        self.f_base_value = LabeledEntry(right, "Base Value (coins)", "10", width=160)

        self.f_key.grid(row=1, column=0, padx=16, pady=6, sticky="ew")
        self.f_name.grid(row=1, column=1, padx=16, pady=6, sticky="ew")
        self.f_rarity.grid(row=2, column=0, padx=16, pady=6, sticky="ew")
        self.f_base_value.grid(row=2, column=1, padx=16, pady=6, sticky="ew")

        ctk.CTkLabel(right, text="FLAVOR TEXT", font=("Consolas", 12), text_color="#888").grid(
            row=3, column=0, columnspan=2, sticky="w", padx=16, pady=(10, 2))
        self.f_description = ctk.CTkTextbox(right, height=70, font=("Consolas", 12))
        self.f_description.grid(row=4, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")

        # weight preview
        self.weight_label = ctk.CTkLabel(right, text="", font=("Consolas", 11), text_color="#888")
        self.weight_label.grid(row=5, column=0, columnspan=2, padx=16, sticky="w")
        self.f_rarity.menu.configure(command=self._update_weight_preview)

        ctk.CTkButton(right, text="Save Fish", command=self._save,
                      font=("Consolas", 13, "bold"), height=36,
                      fg_color="#1B4332", hover_color="#2D6A4F").grid(
            row=6, column=0, columnspan=2, padx=16, pady=12, sticky="ew")

    def _update_weight_preview(self, _=None):
        r = self.f_rarity.get()
        w = RARITY_WEIGHTS.get(r, "?")
        self.weight_label.configure(text=f"Default weight for this rarity: {w}")

    def _load(self):
        data = load_json("fish.json")
        self.fish_data = data.get("fish", [])
        self._refresh_list()

    def _refresh_list(self):
        for w in self.listbox.winfo_children():
            w.destroy()
        for i, fish in enumerate(self.fish_data):
            color = {"common": "#555", "uncommon": "#2E7D32", "rare": "#1565C0",
                     "epic": "#6A1B9A", "legendary": "#E65100"}.get(fish.get("rarity", ""), "#555")
            btn = ctk.CTkButton(
                self.listbox, text=fish.get("name", fish.get("key", "?")),
                anchor="w", font=("Consolas", 12), height=30,
                fg_color="transparent", hover_color="#1E2A3A",
                text_color=color,
                command=lambda idx=i: self._select(idx)
            )
            btn.grid(row=i, column=0, sticky="ew", pady=1)

    def _select(self, index: int):
        self.selected_index = index
        fish = self.fish_data[index]
        self.f_key.set(fish.get("key", ""))
        self.f_name.set(fish.get("name", ""))
        self.f_rarity.set(fish.get("rarity", "common"))
        self.f_base_value.set(fish.get("base_value", 0))
        self.f_description.delete("1.0", "end")
        self.f_description.insert("1.0", fish.get("description", ""))
        self._update_weight_preview()

    def _new(self):
        self.selected_index = -1
        self.f_key.clear(); self.f_name.clear()
        self.f_rarity.set("common"); self.f_base_value.set("10")
        self.f_description.delete("1.0", "end")
        self._update_weight_preview()

    def _save(self):
        key = self.f_key.get()
        if not key:
            messagebox.showerror("Error", "Key is required."); return
        if any(f["key"] == key and i != self.selected_index for i, f in enumerate(self.fish_data)):
            messagebox.showerror("Error", f"Key '{key}' already exists."); return
        try:
            base_value = int(self.f_base_value.get())
        except ValueError:
            messagebox.showerror("Error", "Base value must be an integer."); return

        entry = {
            "key": key,
            "name": self.f_name.get(),
            "rarity": self.f_rarity.get(),
            "base_value": base_value,
            "description": self.f_description.get("1.0", "end").strip()
        }
        if self.selected_index == -1:
            self.fish_data.append(entry)
            self.selected_index = len(self.fish_data) - 1
        else:
            self.fish_data[self.selected_index] = entry

        save_json("fish.json", {"fish": self.fish_data})
        self._refresh_list()
        messagebox.showinfo("Saved", f"Fish '{entry['name']}' saved.")

    def _delete(self):
        if self.selected_index == -1:
            messagebox.showwarning("Nothing selected", "Select a fish first."); return
        name = self.fish_data[self.selected_index].get("name", "?")
        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            self.fish_data.pop(self.selected_index)
            save_json("fish.json", {"fish": self.fish_data})
            self.selected_index = -1
            self._refresh_list()
            self._new()

# ─── Areas Editor Tab ──────────────────────────────────────────────────────────

class AreaFishRow(ctk.CTkFrame):
    """A single row in the area-fish join editor."""
    def __init__(self, master, fish_keys: list, on_remove, **kwargs):
        super().__init__(master, fg_color="#1A2332", corner_radius=6, **kwargs)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.fish_var = ctk.StringVar(value=fish_keys[0] if fish_keys else "")
        self.fish_menu = ctk.CTkOptionMenu(self, values=fish_keys, variable=self.fish_var,
                                           font=("Consolas", 12), width=140)
        self.fish_menu.grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        self.weight = ctk.CTkEntry(self, placeholder_text="weight", width=70, font=("Consolas", 12))
        self.weight.grid(row=0, column=1, padx=4, pady=6, sticky="ew")

        self.min_size = ctk.CTkEntry(self, placeholder_text="min kg", width=70, font=("Consolas", 12))
        self.min_size.grid(row=0, column=2, padx=4, pady=6, sticky="ew")

        self.max_size = ctk.CTkEntry(self, placeholder_text="max kg", width=70, font=("Consolas", 12))
        self.max_size.grid(row=0, column=3, padx=4, pady=6, sticky="ew")

        ctk.CTkButton(self, text="✕", width=28, height=28,
                      fg_color="#4A1515", hover_color="#8B2020",
                      font=("Consolas", 12), command=on_remove).grid(row=0, column=4, padx=6)

    def get_data(self):
        return {
            "fish_key": self.fish_var.get(),
            "weight": int(self.weight.get() or 0),
            "min_size": float(self.min_size.get() or 0),
            "max_size": float(self.max_size.get() or 0),
        }

    def set_data(self, data: dict):
        self.fish_var.set(data.get("fish_key", ""))
        self.weight.delete(0, "end"); self.weight.insert(0, str(data.get("weight", 100)))
        self.min_size.delete(0, "end"); self.min_size.insert(0, str(data.get("min_size", 0.0)))
        self.max_size.delete(0, "end"); self.max_size.insert(0, str(data.get("max_size", 5.0)))

class AreasTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.areas_data: list = []
        self.fish_keys: list = []
        self.selected_index: int = -1
        self.fish_rows: list[AreaFishRow] = []
        self._build()
        self._load()

    def _build(self):
        self.grid_columnconfigure(0, weight=1, minsize=200)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # ── Left panel
        left = ctk.CTkFrame(self, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="AREAS", font=("Consolas", 13, "bold"), text_color="#4FC3F7").grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 4))

        self.listbox = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.listbox.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)
        self.listbox.grid_columnconfigure(0, weight=1)

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=6, pady=8)
        btn_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_row, text="+ New", command=self._new, font=("Consolas", 12),
                      height=30, fg_color="#1E3A5F", hover_color="#2A5298").grid(row=0, column=0, padx=(0,3), sticky="ew")
        ctk.CTkButton(btn_row, text="Delete", command=self._delete, font=("Consolas", 12),
                      height=30, fg_color="#4A1515", hover_color="#8B2020").grid(row=0, column=1, padx=(3,0), sticky="ew")

        # ── Right panel
        right = ctk.CTkFrame(self, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure((0, 1), weight=1)
        right.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(right, text="AREA PROPERTIES", font=("Consolas", 13, "bold"), text_color="#4FC3F7").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 8))

        self.a_key  = LabeledEntry(right, "Key (unique id)", "old_pond")
        self.a_name = LabeledEntry(right, "Display Name", "Old Pond")
        self.a_key.grid(row=1, column=0, padx=16, pady=6, sticky="ew")
        self.a_name.grid(row=1, column=1, padx=16, pady=6, sticky="ew")

        ctk.CTkLabel(right, text="DESCRIPTION", font=("Consolas", 12), text_color="#888").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=16, pady=(6, 2))
        self.a_desc = ctk.CTkTextbox(right, height=55, font=("Consolas", 12))
        self.a_desc.grid(row=3, column=0, columnspan=2, padx=16, pady=(0, 8), sticky="ew")

        # Fish in area header
        fish_header = ctk.CTkFrame(right, fg_color="transparent")
        fish_header.grid(row=4, column=0, columnspan=2, sticky="ew", padx=16, pady=(4, 2))
        fish_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(fish_header, text="FISH IN THIS AREA", font=("Consolas", 12, "bold"), text_color="#4FC3F7").grid(
            row=0, column=0, sticky="w")
        ctk.CTkButton(fish_header, text="+ Add Fish", width=90, height=26,
                      font=("Consolas", 11), fg_color="#1E3A5F", hover_color="#2A5298",
                      command=self._add_fish_row).grid(row=0, column=1)

        # Column headers
        col_hdr = ctk.CTkFrame(right, fg_color="transparent")
        col_hdr.grid(row=5, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 2))
        for i, txt in enumerate(["Fish Key", "Weight", "Min Size", "Max Size"]):
            ctk.CTkLabel(col_hdr, text=txt, font=("Consolas", 11), text_color="#666",
                         width=100).grid(row=0, column=i, sticky="w", padx=6)

        self.fish_scroll = ctk.CTkScrollableFrame(right, fg_color="transparent", height=160)
        self.fish_scroll.grid(row=6, column=0, columnspan=2, padx=16, pady=4, sticky="ew")
        self.fish_scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(right, text="Save Area", command=self._save,
                      font=("Consolas", 13, "bold"), height=36,
                      fg_color="#1B4332", hover_color="#2D6A4F").grid(
            row=7, column=0, columnspan=2, padx=16, pady=12, sticky="ew")

    def _load(self):
        fish_data = load_json("fish.json")
        self.fish_keys = [f["key"] for f in fish_data.get("fish", [])]
        if not self.fish_keys:
            self.fish_keys = ["(no fish — add in Fish tab)"]
        area_data = load_json("areas.json")
        self.areas_data = area_data.get("areas", [])
        self._refresh_list()

    def refresh_fish_keys(self):
        """Call this when fish tab saves, to keep keys in sync."""
        fish_data = load_json("fish.json")
        self.fish_keys = [f["key"] for f in fish_data.get("fish", [])]

    def _refresh_list(self):
        for w in self.listbox.winfo_children():
            w.destroy()
        for i, area in enumerate(self.areas_data):
            btn = ctk.CTkButton(
                self.listbox, text=area.get("name", area.get("key", "?")),
                anchor="w", font=("Consolas", 12), height=30,
                fg_color="transparent", hover_color="#1E2A3A",
                command=lambda idx=i: self._select(idx)
            )
            btn.grid(row=i, column=0, sticky="ew", pady=1)

    def _select(self, index: int):
        self.selected_index = index
        area = self.areas_data[index]
        self.a_key.set(area.get("key", ""))
        self.a_name.set(area.get("name", ""))
        self.a_desc.delete("1.0", "end")
        self.a_desc.insert("1.0", area.get("description", ""))
        self._clear_fish_rows()
        for entry in area.get("fish", []):
            self._add_fish_row(entry)

    def _new(self):
        self.selected_index = -1
        self.a_key.clear(); self.a_name.clear()
        self.a_desc.delete("1.0", "end")
        self._clear_fish_rows()

    def _clear_fish_rows(self):
        for row in self.fish_rows:
            row.destroy()
        self.fish_rows.clear()

    def _add_fish_row(self, data: dict = None):
        if not self.fish_keys:
            return
        row = AreaFishRow(
            self.fish_scroll,
            fish_keys=self.fish_keys,
            on_remove=lambda r=None: self._remove_fish_row(row)
        )
        row.grid(row=len(self.fish_rows), column=0, sticky="ew", pady=3)
        if data:
            row.set_data(data)
        elif self.fish_keys:
            row.set_data({"fish_key": self.fish_keys[0], "weight": 100, "min_size": 0.5, "max_size": 5.0})
        self.fish_rows.append(row)

    def _remove_fish_row(self, row: AreaFishRow):
        row.destroy()
        self.fish_rows.remove(row)

    def _save(self):
        key = self.a_key.get()
        if not key:
            messagebox.showerror("Error", "Key is required."); return
        if any(a["key"] == key and i != self.selected_index for i, a in enumerate(self.areas_data)):
            messagebox.showerror("Error", f"Key '{key}' already exists."); return

        fish_entries = []
        for row in self.fish_rows:
            try:
                fish_entries.append(row.get_data())
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid fish row data: {e}"); return

        entry = {
            "key": key,
            "name": self.a_name.get(),
            "description": self.a_desc.get("1.0", "end").strip(),
            "fish": fish_entries
        }
        if self.selected_index == -1:
            self.areas_data.append(entry)
            self.selected_index = len(self.areas_data) - 1
        else:
            self.areas_data[self.selected_index] = entry

        save_json("areas.json", {"areas": self.areas_data})
        self._refresh_list()
        messagebox.showinfo("Saved", f"Area '{entry['name']}' saved.")

    def _delete(self):
        if self.selected_index == -1:
            messagebox.showwarning("Nothing selected", "Select an area first."); return
        name = self.areas_data[self.selected_index].get("name", "?")
        if messagebox.askyesno("Delete", f"Delete area '{name}'?"):
            self.areas_data.pop(self.selected_index)
            save_json("areas.json", {"areas": self.areas_data})
            self.selected_index = -1
            self._refresh_list()
            self._new()

# ─── Raw JSON Tab ──────────────────────────────────────────────────────────────

class RawJsonTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top.grid_columnconfigure(1, weight=1)

        self.file_var = ctk.StringVar(value="fish.json")
        ctk.CTkOptionMenu(top, values=["fish.json", "areas.json"],
                          variable=self.file_var, font=("Consolas", 13), width=160).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(top, text="Load", font=("Consolas", 12), width=80,
                      fg_color="#1E3A5F", hover_color="#2A5298",
                      command=self._load).grid(row=0, column=1, sticky="w", padx=(0, 6))
        ctk.CTkButton(top, text="Save Raw", font=("Consolas", 12), width=90,
                      fg_color="#1B4332", hover_color="#2D6A4F",
                      command=self._save).grid(row=0, column=2)

        self.editor = ctk.CTkTextbox(self, font=("Consolas", 13), wrap="none")
        self.editor.grid(row=1, column=0, sticky="nsew")

    def _load(self):
        data = load_json(self.file_var.get())
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", json.dumps(data, indent=2))

    def _save(self):
        try:
            data = json.loads(self.editor.get("1.0", "end"))
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", str(e)); return
        save_json(self.file_var.get(), data)
        messagebox.showinfo("Saved", f"{self.file_var.get()} saved.")

# ─── App Shell ─────────────────────────────────────────────────────────────────

class EditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bot Seed Editor")
        self.geometry("980x680")
        self.minsize(800, 560)
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, height=48, corner_radius=0, fg_color="#0D1B2A")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header, text="⚙  SEED EDITOR", font=("Consolas", 15, "bold"),
                     text_color="#4FC3F7").grid(row=0, column=0, padx=16, pady=12, sticky="w")
        self.status = ctk.CTkLabel(header, text=f"seed dir: {SEED_DIR}",
                                   font=("Consolas", 11), text_color="#555")
        self.status.grid(row=0, column=1, padx=16, sticky="e")

        # Tab view
        tabs = ctk.CTkTabview(self, anchor="nw",
                              segmented_button_selected_color="#1565C0",
                              segmented_button_selected_hover_color="#1976D2")
        tabs.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)

        tabs.add("Fish")
        tabs.add("Areas")
        tabs.add("Raw JSON")

        tabs.tab("Fish").grid_columnconfigure(0, weight=1)
        tabs.tab("Fish").grid_rowconfigure(0, weight=1)
        tabs.tab("Areas").grid_columnconfigure(0, weight=1)
        tabs.tab("Areas").grid_rowconfigure(0, weight=1)
        tabs.tab("Raw JSON").grid_columnconfigure(0, weight=1)
        tabs.tab("Raw JSON").grid_rowconfigure(0, weight=1)

        self.fish_tab  = FishTab(tabs.tab("Fish"))
        self.areas_tab = AreasTab(tabs.tab("Areas"))
        self.raw_tab   = RawJsonTab(tabs.tab("Raw JSON"))

        self.fish_tab.grid(row=0, column=0, sticky="nsew")
        self.areas_tab.grid(row=0, column=0, sticky="nsew")
        self.raw_tab.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = EditorApp()
    app.mainloop()