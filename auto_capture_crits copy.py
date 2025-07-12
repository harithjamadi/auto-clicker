import time
import numpy as np
import pyautogui
from PIL import ImageGrab
from pynput import keyboard, mouse
import threading
import sys
import requests
import webcolors
import os
import easyocr
from dotenv import load_dotenv

reader = easyocr.Reader(['en'])

# === CONFIG ===
pos_main = (995, 459)
pos_check = (1117, 210)

color_check_allowed = [
    (87, 98, 104),  # gray - common
]

attack_sequence = 2

capture_rate = []
rare_rate = ['17', '17%', '18', '18%', '20%', '20%']
common_rate = ['J0%', 'J0%0', '20', '20%', '27', '27%', '28', '28%', '30', '30%']

# === CONTROL FLAGS ===
start_program = False
paused = False
exit_program = False
config_mode = False
mouse_listener = None

# === UTILS ===
def colors_are_close(c1, c2, tolerance=10):
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

def get_pixel_color(x, y):
    img = ImageGrab.grab().load()
    return img[x, y]

def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def get_color_name(rgb_tuple):
    try:
        hex_value = webcolors.rgb_to_hex(rgb_tuple)
        return webcolors.hex_to_name(hex_value)
    except ValueError:
        return closest_color(rgb_tuple)

def send_telegram_message(message):
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    try:
        requests.post(url, data=payload)
        print("Telegram notification sent.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

# === MOUSE CONFIG ===
def on_click(x, y, button, pressed):
    global pos_main, config_mode
    if pressed and config_mode:
        img = ImageGrab.grab().load()
        color = img[x, y]
        print(f"Configured Search Position at ({x}, {y}) - Color: RGB{color}")
        pos_main = (x, y)
        config_mode = False
        return False  # stop listener

def start_mouse_listener():
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()

# === INPUT LISTENER ===
def on_key_press(key):
    global start_program, exit_program, paused, config_mode
    try:
        if key.char == '`':
            if not config_mode:
                paused = not paused
                print("Resuming program." if not paused else "Pausing program.")
                if not start_program:
                    start_program = True
        elif key.char == '-':
            print("- pressed. Pausing program.")
            paused = True
        elif key.char == '=':
            if not start_program:
                print("= pressed. Configure Crits Search Position: Click once to set position")
                config_mode = True
                threading.Thread(target=start_mouse_listener, daemon=True).start()
    except AttributeError:
        if key == keyboard.Key.esc:
            print("ESC pressed. Exiting immediately.")
            exit_program = True
            os._exit(0)

def wait_for_capture_opportunity():
    while True:
        capture_color = get_pixel_color(*(1002, 282))
        if colors_are_close(capture_color, (210, 115, 0), tolerance=0):
            pyautogui.click(959, 276)
            print("Attempt to capture Crits...")
            break
        elif get_pixel_color(*(953, 464)) == (255, 255, 255):
            print("Crits died...")
            break
        time.sleep(0.5)

def post_capture_check():
    while True:
        time.sleep(6)
        if colors_are_close(get_pixel_color(*(1043, 487)), (219, 132, 56), tolerance=0):
            print("Crits successfully captured !")
            for pos in [(944, 565), (944, 565), (944, 692), (944, 692), (915, 597)]:
                pyautogui.click(*pos)
                time.sleep(2)
            # check for level up status
            if colors_are_close(get_pixel_color(*(897, 591)), (166, 166, 166), tolerance=0):
                pyautogui.click(*(959, 635))
                time.sleep(1)
            break
        elif get_pixel_color(*(953, 464)) == (255, 255, 255):
            print("Crits died...")
            pyautogui.click(944, 692)
            time.sleep(2)
            break
        else:
            print("Crits failed to be captured, kill the Crits")
            kill_crits()
            break

def kill_crits():
    while not exit_program:
        if colors_are_close(get_pixel_color(960, 201), (237, 128, 25), tolerance=50):
            pyautogui.click(719, 785)
            time.sleep(0.5)
        else:
            break
    while not exit_program:
        if get_pixel_color(953, 464) == (255, 255, 255):
            pyautogui.click(944, 692)
            time.sleep(2)
            break

def run_attack_sequence():
    i = 0
    while i != attack_sequence:
        attack_color = get_pixel_color(*(638, 788))
        if any(colors_are_close(attack_color, c, tolerance=0) for c in [(226, 237, 255), (240, 186, 52)]):
            pyautogui.click(638, 788)
            print(f"#{i + 1} Attack")
            i += 1
        else:
            time.sleep(0.5)
        time.sleep(5)
    time.sleep(2)

def auto_clicker():
    global exit_program, paused, capture_rate

    while not start_program and not exit_program:
        time.sleep(1)

    while not exit_program:
        if paused:
            time.sleep(1)
            continue

        pyautogui.moveTo(*pos_main)
        time.sleep(1.5)
        pyautogui.mouseDown()
        time.sleep(0.1)
        pyautogui.mouseUp()
        print(f"Search for Crits at {pos_main}")

        if colors_are_close(get_pixel_color(1270, 731), (39, 62, 82), tolerance=30):
            time.sleep(3)
            color_check_now = get_pixel_color(*pos_check)
            print("Checking Crits rarity...")

            if any(colors_are_close(color_check_now, c, tolerance=20) for c in color_check_allowed):
                capture_rate = rare_rate if colors_are_close(color_check_now, (54, 87, 213), tolerance=20) else common_rate
                img_np = np.array(ImageGrab.grab(bbox=(932, 285, 990, 312)))
                results = reader.readtext(img_np)
                print("OCR Results:")
                text = next((txt.strip() for (_, txt, _) in results), None)
                print("Crits rating is ", text)
                if text and any(val in text for val in capture_rate):
                    print('🎉 A+ crits or above found, initiate to capture')
                    run_attack_sequence()
                    wait_for_capture_opportunity()
                    post_capture_check()
                else:
                    kill_crits()
            else:
                color_name = get_color_name(color_check_now)
                print(f"⚠️ Miscrit rarity of {color_name}")
                run_attack_sequence()
                wait_for_capture_opportunity()
                post_capture_check()

if __name__ == "__main__":
    print("Ready. Press = to set search position, ` to start/resume, '-' to pause, ESC to quit.")
    key_thread = threading.Thread(target=lambda: keyboard.Listener(on_press=on_key_press).run(), daemon=True)
    key_thread.start()
    auto_clicker()

