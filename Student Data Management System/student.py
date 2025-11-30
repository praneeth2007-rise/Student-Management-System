import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB = "students.db"

# ---------------- Database ----------------
class StudentDB:
    def __init__(self):
        self._create()

    def _create(self):
        conn = sqlite3.connect(DB)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, roll TEXT UNIQUE,
                class TEXT, phone TEXT, address TEXT
            );
        """)
        conn.commit(); conn.close()

    def add(self, n, r, c, p, a):
        conn = sqlite3.connect(DB)
        conn.execute(
            "INSERT INTO students(name,roll,class,phone,address) VALUES(?,?,?,?,?)",
            (n, r, c, p, a)
        )
        conn.commit(); conn.close()

    def update(self, sid, n, r, c, p, a):
        conn = sqlite3.connect(DB)
        conn.execute(
            "UPDATE students SET name=?, roll=?, class=?, phone=?, address=? WHERE id=?",
            (n, r, c, p, a, sid)
        )
        conn.commit(); conn.close()

    def delete(self, sid):
        conn = sqlite3.connect(DB)
        conn.execute("DELETE FROM students WHERE id=?", (sid,))
        conn.commit(); conn.close()

    def fetch_all(self):
        conn = sqlite3.connect(DB)
        data = conn.execute("SELECT * FROM students ORDER BY roll").fetchall()
        conn.close()
        return data

    def search(self, field, q):
        conn = sqlite3.connect(DB)
        data = conn.execute(
            f"SELECT * FROM students WHERE {field} LIKE ?",
            (f"%{q}%",)
        ).fetchall()
        conn.close()
        return data


# ---------------- GUI ----------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = StudentDB()
        self.title("Student Manager")
        self.geometry("780x520")

        self.id = None
        self.build()
        self.load()

    def build(self):
        f = ttk.Frame(self)
        f.pack(fill="x", padx=10, pady=10)

        self.name = tk.StringVar()
        self.roll = tk.StringVar()
        self.cls  = tk.StringVar()
        self.ph   = tk.StringVar()
        self.add  = tk.StringVar()

        labels = ["Name", "Roll", "Class", "Phone", "Address"]
        vars   = [self.name, self.roll, self.cls, self.ph, self.add]

        for i, (t, v) in enumerate(zip(labels, vars)):
            ttk.Label(f, text=t).grid(row=i//2, column=(i%2)*2, sticky="w")
            ttk.Entry(f, textvariable=v, width=28).grid(row=i//2, column=(i%2)*2 + 1, padx=5, pady=4)

        # Buttons
        b = ttk.Frame(self)
        b.pack(pady=5)
        self.btn = ttk.Button(b, text="Add", command=self.save)
        self.btn.pack(side="left", padx=5)
        ttk.Button(b, text="Delete", command=self.delete).pack(side="left", padx=5)
        ttk.Button(b, text="Clear", command=self.clear).pack(side="left", padx=5)

        # Search
        s = ttk.Frame(self)
        s.pack(fill="x", padx=10)
        self.sf = tk.StringVar(value="name")
        self.sq = tk.StringVar()
        ttk.Combobox(
            s, textvariable=self.sf,
            values=["name", "roll", "class", "phone", "address"],
            width=10
        ).pack(side="left")

        ttk.Entry(s, textvariable=self.sq, width=35).pack(side="left", padx=5)
        ttk.Button(s, text="Search", command=self.search).pack(side="left")
        ttk.Button(s, text="Show All", command=self.load).pack(side="left", padx=5)

        # Table
        cols = ("id", "name", "roll", "class", "phone", "address")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")

        for c in cols:
            self.tree.heading(c, text=c.title())

        # Column widths (added)
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=180)
        self.tree.column("roll", width=90, anchor="center")
        self.tree.column("class", width=90, anchor="center")
        self.tree.column("phone", width=120, anchor="center")
        self.tree.column("address", width=250)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.select)

    # ---------------- Actions ----------------
    def load(self):
        self.tree.delete(*self.tree.get_children())
        for r in self.db.fetch_all():
            self.tree.insert("", "end", values=r)

    def save(self):
        n, r, c, p, a = self.name.get(), self.roll.get(), self.cls.get(), self.ph.get(), self.add.get()

        if not n or not r:
            messagebox.showwarning("Warning", "Name and Roll required")
            return

        try:
            if self.id is None:
                self.db.add(n, r, c, p, a)
            else:
                self.db.update(self.id, n, r, c, p, a)

            self.clear()
            self.load()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete(self):
        if self.id is None:
            return
        self.db.delete(self.id)
        self.clear()
        self.load()

    def search(self):
        q = self.sq.get()
        f = self.sf.get()
        rows = self.db.search(f, q)
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=r)

    def select(self, _):
        item = self.tree.item(self.tree.selection()[0])["values"]
        self.id, n, r, c, p, a = item
        self.name.set(n)
        self.roll.set(r)
        self.cls.set(c)
        self.ph.set(p)
        self.add.set(a)
        self.btn.config(text="Update")

    def clear(self):
        self.id = None
        for v in (self.name, self.roll, self.cls, self.ph, self.add):
            v.set("")
        self.btn.config(text="Add")


# ---------------- Run ----------------
App().mainloop()