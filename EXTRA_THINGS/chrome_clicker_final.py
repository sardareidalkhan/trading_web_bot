import time
import threading
import keyboard
import win32gui
import win32api
import win32con

clicking = False
click_pos = (0, 0)

def get_mouse_position():
    return win32api.GetCursorPos()

def get_foreground_window():
    return win32gui.GetForegroundWindow()

def click_at(hwnd, x, y):
    lParam = win32api.MAKELONG(x, y)
    win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, lParam)

def click_loop():
    global clicking
    hwnd = None

    while True:
        if clicking:
            hwnd = get_foreground_window()
            click_at(hwnd, *click_pos)
        time.sleep(1)

def toggle_clicking():
    global clicking, click_pos
    if not clicking:
        click_pos = get_mouse_position()
        print(f"Clicking started at: {click_pos}")
        clicking = True
    else:
        print("Clicking stopped.")
        clicking = False

print("Move mouse to point to click, then press SPACE to start.")
print("Press SPACE again to stop. Press ESC to quit.")

keyboard.add_hotkey('space', toggle_clicking)
threading.Thread(target=click_loop, daemon=True).start()
keyboard.wait('esc')
