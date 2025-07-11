import time
import numpy as np
import pyautogui
from PIL import ImageGrab
from pynput import keyboard
import threading
import sys
import requests
import webcolors
import os
import easyocr
from dotenv import load_dotenv

reader = easyocr.Reader(['en'])

# === CONFIG ===
pos_main = (995, 459)  # change based on crits
pos_check = (1117, 210)

color_check_allowed = [
    (87, 98, 104),   # gray - common
    # (54, 87, 213)    # blue - rare
]

attack_sequence = 2

capture_rate = []
rare_rate = ['17', '17%', '18', '18%', '20%', '20%']
common_rate = ['3','J0%', 'J0%0', '20', '20%', '27', '27%', '28', '28%', '30', '30%']

pos_extra1 = (597, 713)
pos_extra2 = (917, 610)

# === CONTROL FLAGS ===
start_program = False
paused = False
exit_program = False

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

# === INPUT LISTENER ===
def on_key_press(key):
    global start_program, exit_program, paused
    try:
        if key.char == '`':
            if paused:
                print("Resuming program.")
                paused = False
            else:
                print("` pressed. Starting program.")
                start_program = True
        elif key.char == '-':
            print("- pressed. Pausing program.")
            paused = True
    except AttributeError:
        if key == keyboard.Key.esc:
            print("ESC pressed. Exiting immediately.")
            exit_program = True
            os._exit(0)

# === MAIN LOOP ===
def auto_clicker():
    global exit_program, paused

    while not start_program and not exit_program:
        time.sleep(1)

    while not exit_program:
        if paused:
            time.sleep(1)
            continue

        flag = True
        while flag and not exit_program and not paused:
            pyautogui.moveTo(*pos_main)
            time.sleep(1.5)
            pyautogui.mouseDown()
            time.sleep(0.1)
            pyautogui.mouseUp()
            print(f"Search for Crits at {pos_main}")

            color_check_now = get_pixel_color(1270, 731)
            print(f"Checking battle status...")

            if colors_are_close(color_check_now, (39, 62, 82), tolerance=30):
                flag = False
                break

        if exit_program or paused:
            continue

        time.sleep(3)

        color_check_now = get_pixel_color(*pos_check)
        print(f"Checking Crits rarity...")

        if any(colors_are_close(color_check_now, c, tolerance=20) for c in color_check_allowed):

            if colors_are_close(color_check_now, (54, 87, 213), tolerance=20):
                capture_rate = rare_rate
            else:
                capture_rate = common_rate

            img = ImageGrab.grab(bbox=(932, 285, 990, 312))
            img_np = np.array(img)
            results = reader.readtext(img_np)
            print("OCR Results:")

            text = None
            if results:
                for (bbox, txt, prob) in results:
                    print(f"Detected: '{txt}' (Confidence: {prob:.2f}) at {bbox}")
                    text = txt.strip()

            if text is not None and any(val in text for val in capture_rate):
                msg = '🎉 A+ crits or above found, initiate to capture'
                print(msg)
                # send_telegram_message(msg)

                i = 0

                while (i != attack_sequence):
                    attack_color = get_pixel_color(*(987, 789))
                    if colors_are_close(attack_color, (135, 135, 135), tolerance=5):
                        pyautogui.click(722, 782)
                        # time.sleep(0.5)
                        # pyautogui.click(722, 782)
                        print(f"#{i + 1} Attack")
                        i = i + 1
                    else:
                        time.sleep(0.5)

                while True:
                    capture_color = get_pixel_color(*(1002, 282))
                    if colors_are_close(capture_color, (210, 115, 0), tolerance=20):
                        pyautogui.click(959, 276)
                        # time.sleep(0.5)
                        # pyautogui.click(959, 276)
                        print("Attempt to capture Crits...")
                        break
                    # in a case the Crits being 1-shotted
                    elif get_pixel_color(*(953, 464)) == (255, 255, 255):
                        print("Crits died...")
                        break
                    else:
                        time.sleep(0.5)

                while(True):
                    time.sleep(6)
                    color_check_now = get_pixel_color(*(1043, 487))
                    if colors_are_close(color_check_now, (219, 132, 56), tolerance=0):
                        print("Crits successfully captured !")
                        time.sleep(2)

                        pyautogui.click(944, 565)
                        time.sleep(0.5)
                        pyautogui.click(944, 565)
                        time.sleep(2)

                        pyautogui.click(944, 692)
                        time.sleep(0.5)
                        pyautogui.click(944, 692)
                        time.sleep(2)

                        pyautogui.click(915, 597)
                        time.sleep(0.5)
                        break
                    # in a case the Crits being 1-shotted
                    elif get_pixel_color(*(953, 464)) == (255, 255, 255):
                        print("Crits died...")
                        pyautogui.click(944, 692)
                        time.sleep(2)
                        break
                    else:
                        print("Crits failed to be captured, kill the Crits")
                        while not exit_program:
                            color = get_pixel_color(960, 201)
                            if colors_are_close(color, (237, 128, 25), tolerance=50):
                                pyautogui.click(719, 785)
                                time.sleep(0.5)
                            else:
                                break

                        while not exit_program:
                            color = get_pixel_color(*(953, 464)) # check hijau
                            if color == (255, 255, 255):
                                pyautogui.click(944, 692)
                                time.sleep(2)
                                break

                        break
            else:
                while not exit_program:
                    color = get_pixel_color(960, 201)
                    if colors_are_close(color, (237, 128, 25), tolerance=50):
                        pyautogui.click(719, 785)
                        time.sleep(0.5)
                    else:
                        break

                while not exit_program:
                    color = get_pixel_color(809, 320)
                    if color == (107, 138, 19):
                        pyautogui.click(966, 694)
                        time.sleep(0.5)
                        break
        else:
            color_name = get_color_name(color_check_now)
            msg = f"⚠️ Miscrit rarity of {color_name}"
            print(msg)
            # send_telegram_message(msg)
            i = 0

            while (i != attack_sequence):
                attack_color = get_pixel_color(*(987, 789))
                if colors_are_close(attack_color, (135, 135, 135), tolerance=5):
                    pyautogui.click(722, 782)
                    # time.sleep(0.5)
                    # pyautogui.click(722, 782)
                    print(f"#{i + 1} Attack")
                    i = i + 1
                else:
                    time.sleep(0.5)

            while True:
                capture_color = get_pixel_color(*(1002, 282))
                if colors_are_close(capture_color, (210, 115, 0), tolerance=20):
                    pyautogui.click(959, 276)
                    # time.sleep(0.5)
                    # pyautogui.click(959, 276)
                    print("Attempt to capture Crits...")
                    break
                else:
                    time.sleep(0.5)

            while(True):
                time.sleep(6)
                color_check_now = get_pixel_color(*(1043, 487))
                if colors_are_close(color_check_now, (219, 132, 56), tolerance=0):
                    print("Crits successfully captured !")
                    time.sleep(2)

                    pyautogui.click(944, 565)
                    time.sleep(0.5)
                    pyautogui.click(944, 565)
                    time.sleep(2)

                    pyautogui.click(944, 692)
                    time.sleep(0.5)
                    pyautogui.click(944, 692)
                    time.sleep(2)

                    pyautogui.click(915, 597)
                    time.sleep(0.5)
                    break

                else:
                    print("Crits failed to be captured, kill the Crits")
                    while not exit_program:
                        color = get_pixel_color(960, 201)
                        if colors_are_close(color, (237, 128, 25), tolerance=50):
                            pyautogui.click(719, 785)
                            time.sleep(0.5)
                        else:
                            break

                    while not exit_program:
                        color = get_pixel_color(809, 320)
                        if color == (107, 138, 19):
                            pyautogui.click(966, 694)
                            time.sleep(0.5)
                            break

                    break

# === ENTRY POINT ===
if __name__ == "__main__":
    print("Ready. Press ` to start/resume, '-' to pause, ESC to quit.")

    key_thread = threading.Thread(target=lambda: keyboard.Listener(on_press=on_key_press).run(), daemon=True)
    key_thread.start()

    auto_clicker()
