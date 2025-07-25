# thread_line_overlay.py

import tkinter as tk
import keyboard

# === Settings ===
line_color = "red"          # Thread color (you can change to green, blue, etc.)
initial_x = 687             # Starting x-position of the line (in pixels)
line_thickness = 1          # Starting line thickness

# === GUI Setup ===
root = tk.Tk()
root.title("Thread Line Overlay")
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
root.attributes("-topmost", True)
root.attributes("-transparentcolor", "black")
root.overrideredirect(True)  # Removes title bar
canvas = tk.Canvas(root, bg='black', highlightthickness=0)
canvas.pack(fill="both", expand=True)

# === Draw the initial vertical line ===
line_id = canvas.create_line(initial_x, 0, initial_x, root.winfo_screenheight(),
                             fill=line_color, width=line_thickness)

# === Move line left/right & adjust thickness ===
x = initial_x
thickness = line_thickness

def update_line():
    canvas.coords(line_id, x, 0, x, root.winfo_screenheight())
    canvas.itemconfig(line_id, width=thickness)

def move_left():
    global x
    x -= 5
    update_line()

def move_right():
    global x
    x += 5
    update_line()

def thinner():
    global thickness
    if thickness > 1:
        thickness -= 1
        update_line()

def thicker():
    global thickness
    thickness += 1
    update_line()

def quit_overlay():
    root.destroy()

# === Hotkeys ===
keyboard.add_hotkey('left', move_left)
keyboard.add_hotkey('right', move_right)
keyboard.add_hotkey('up', thicker)
keyboard.add_hotkey('down', thinner)
keyboard.add_hotkey('esc', quit_overlay)

print("🧵 Thread Line Overlay started!")
print("← → to move line | ↑ ↓ to adjust thickness | Esc to exit")

root.mainloop()
