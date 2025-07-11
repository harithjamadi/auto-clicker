from PIL import ImageGrab
import pyautogui
import time

def get_pixel_color(x, y):
    img = ImageGrab.grab().load()
    return img[x, y]

pos = (944, 692)

time.sleep(2)  # Gives you time to switch window
pyautogui.moveTo(*pos)

print(get_pixel_color(*pos))
