"""Build a PDF packet from selected pages in multiple documents."""
import os
import re
import shutil
import tempfile
import tkinter as tk
from contextlib import ExitStack
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from pypdf import PdfReader, PdfWriter


def pages(expression, count):
    if expression.strip().lower() == "all":
        return list(range(count))
    selected = []
    for token in expression.split(","):
        match = re.fullmatch(r"\s*(\d+)(?:\s*-\s*(\d+))?\s*", token)
        if not match:
            raise ValueError("Use all, or page numbers and ranges such as 1, 4-6.")
        first = int(match[1])
        last = int(match[2] or first)
        if not 1 <= first <= last <= count:
            raise ValueError(f"Range outside pages 1–{count}: {token.strip()}")
        selected.extend(range(first - 1, last))
    return selected


def assemble(entries, target):
    writer = PdfWriter()
    target = Path(target)
    with ExitStack() as stack:
        for path, expression in entries:
            reader = PdfReader(stack.enter_context(Path(path).open("rb")))
            if reader.is_encrypted:
                raise ValueError(f"Open an unlocked copy of {Path(path).name}.")
            for index in pages(expression, len(reader.pages)):
                writer.add_page(reader.pages[index])
        if not len(writer.pages):
            raise ValueError("Add at least one page.")
        # Stage the complete PDF before creating the user-visible file.
        with tempfile.TemporaryFile(dir=target.parent) as staged:
            writer.write(staged)
            staged.seek(0)
            with target.open("xb") as output:
                try:
                    shutil.copyfileobj(staged, output)
                    output.flush()
                    os.fsync(output.fileno())
                except OSError:
                    output.close()
                    target.unlink(missing_ok=True)
                    raise
    return len(writer.pages)


def main():
    root = tk.Tk()
    root.title("PDF Packet Desk")
    root.geometry("820x490")
    panel = ttk.Frame(root, padding=18)
    panel.pack(fill="both", expand=True)
    ttk.Label(panel, text="PDF Packet Desk", font=("Segoe UI", 21, "bold")).pack(anchor="w")
    ttk.Label(panel, text="Add PDFs in reading order. Select a row to edit its page range.").pack(anchor="w", pady=(0, 12))
    table = ttk.Treeview(panel, columns=("file", "pages"), show="headings", selectmode="browse")
    table.heading("file", text="Source document")
    table.heading("pages", text="Included pages")
    table.column("file", width=450)
    table.pack(fill="both", expand=True)
    sources = {}
    def add():
        for path in filedialog.askopenfilenames(filetypes=[("PDF documents", "*.pdf")]):
            row = table.insert("", "end", values=(Path(path).name, "all"))
            sources[row] = path
            table.selection_set(row)
    def edit(event=None):
        for row in table.selection():
            selection = simpledialog.askstring("Page selection", "Pages in output order (all, or e.g. 4, 1-3):",
                                               initialvalue=table.set(row, "pages"), parent=root)
            if selection is not None:
                table.set(row, "pages", selection)
    def move(delta):
        for row in table.selection():
            index = max(0, min(len(table.get_children()) - 1, table.index(row) + delta))
            table.move(row, "", index)
    def remove():
        for row in table.selection():
            table.delete(row)
            del sources[row]
    def save():
        entries = [(sources[r], table.set(r, "pages")) for r in table.get_children()]
        if not entries:
            messagebox.showinfo("Add documents", "Add a PDF first.")
            return
        target = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF document", "*.pdf")])
        if not target:
            return
        try:
            count = assemble(entries, target)
            messagebox.showinfo("Packet saved", f"Saved {count} pages to {target}")
        except FileExistsError:
            messagebox.showerror("Choose a new filename", "The destination already exists.")
        except Exception as error:
            messagebox.showerror("Could not assemble packet", str(error))
    bar = ttk.Frame(panel)
    bar.pack(fill="x", pady=10)
    for label, action in [("Add PDFs", add), ("Edit pages", edit), ("Move up", lambda: move(-1)),
                          ("Move down", lambda: move(1)), ("Remove", remove), ("Save packet", save)]:
        ttk.Button(bar, text=label, command=action).pack(side="left", padx=2)
    table.bind("<Double-1>", edit)
    root.mainloop()


if __name__ == "__main__":
    main()
