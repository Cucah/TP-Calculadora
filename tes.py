from pathlib import Path
import tkinter as tk

BASE_DIR = Path(__file__).resolve().parent
icon_path = BASE_DIR / "icon.png"

print("Caminho:", icon_path)
print("Existe:", icon_path.exists())
print("É arquivo:", icon_path.is_file())

root = tk.Tk()

icon = tk.PhotoImage(file=str(icon_path))
root.iconphoto(True, icon)

root.mainloop()