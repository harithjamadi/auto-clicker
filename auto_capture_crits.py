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

# Positions and expected colors
# pos_main = (935, 581)
# pos_main = (916, 582) # for light ignios
# pos_main = (929, 550) # for light ignios
# pos_main = (942, 428) #foil waddle
pos_main = (952, 414) # dslithero
# pos_main = (983, 338) # for windy need to fix

# pos_check = (1341, 115)
pos_check = (1117, 210)

color_check_allowed = [
    (87, 98, 104),   # gray - common
    (54, 87, 213)    # blue - rare
]
# color_check_gray = (87, 98, 104) #common
# color_check_blue = (54, 87, 213) #rare
# color_check = (253, 158, 0) #legend

# pos_extra1 = (466, 795)
# color_extra1 = (53, 70, 90)
pos_extra1 = (597, 713)


# pos_extra2 = (899, 652)
# color_extra2 = (125, 129, 127)
pos_extra2 = (917, 610)


# Control flags
start_program = False
exit_program = False

def colors_are_close(c1, c2, tolerance=10):
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

def get_pixel_color(x, y):
    img = ImageGrab.grab().load()
    return img[x, y]

def on_key_press(key):
    global start_program, exit_program
    try:
        if key.char == '`':
            print(" pressed. Starting program.")
            start_program = True
    except AttributeError:
        if key == keyboard.Key.esc:
            print("ESC pressed. Exiting...")
            exit_program = True
            return False

def auto_clicker():
    global exit_program
    while not start_program and not exit_program:
        time.sleep(4)

        while not exit_program and start_program:
            flag = True

            while flag and not exit_program:
                pyautogui.moveTo(*pos_main)
                time.sleep(1.5)
                pyautogui.mouseDown()
                time.sleep(0.1)
                pyautogui.mouseUp()
                print(f"Clicked {pos_main}")

                color_check_now = get_pixel_color(*(1270, 731))
                print(f"Checking {(1270, 731)} -> RGB{color_check_now}")

                if colors_are_close(color_check_now, (39, 62, 82), tolerance=20):
                    flag = False
                    break

            # if exit_program:
            #     break

    #     time.sleep(1)
    #     flag = True

    #     while flag:
    #         pyautogui.click(*pos_main)
    #         print(f"Clicked {pos_main}")
    #         time.sleep(0.5)

    #         color_check_now = get_pixel_color(*pos_check)

    #         if colors_are_close(color_check_now, color_check, tolerance=20):
    #             flag = False


        # for _ in range(100):
        #     pyautogui.click(*pos_main)
        #     print(f"Clicked {pos_main}")
        #     time.sleep(0.5)

            time.sleep(3) 

            # Check color at pos_check
            color_check_now = get_pixel_color(*pos_check)
            print(f"Checking {pos_check} -> {color_check_now}")

            if any(colors_are_close(color_check_now, c, tolerance=20) for c in color_check_allowed):

                img = ImageGrab.grab(bbox=(932, 285, 990, 312))
                img_np = np.array(img)

                results = reader.readtext(img_np)
                print("OCR Results:")
                if results:
                    for (bbox, text, prob) in results:
                        print(f"Detected: '{text}' (Confidence: {prob:.2f}) at {bbox}")
                else:
                    print("No text detected.")

                if text == '27%' or text == '17%':
                    msg = '🎉 S+ crits found, initiate to capture'
                    print(msg)
                    send_telegram_message(msg)
                    pyautogui.click(*(722, 782))
                    time.sleep(0.5)
                    pyautogui.click(*(722, 782))

                    print(f"Clicked {(722, 782)}")
                    time.sleep(7)

                    pyautogui.click(*(959, 276))
                    time.sleep(0.5)
                    pyautogui.click(*(959, 276))

                    print(f"Clicked {(959, 276)}")
                    time.sleep(5)

                    color_check_now = get_pixel_color(*(900, 559))
                    print(color_check_now)
                    if colors_are_close(color_check_now, (205, 111, 21), tolerance=20):
                        pyautogui.click(*(944, 565))
                        time.sleep(0.5)
                        pyautogui.click(*(944, 565))

                        print(f"Clicked {(944, 565)}")
                        time.sleep(3)

                        pyautogui.click(*(944, 692))
                        time.sleep(0.5)
                        pyautogui.click(*(944, 692))

                        print(f"Clicked {(944, 692)}")
                        time.sleep(3)

                        pyautogui.click(*(915, 597))
                        time.sleep(0.5)

                        print(f"Clicked {(915, 597)}")
                        time.sleep(3)
                    else:
                        time.sleep(3)
                        pyautogui.click(*pos_extra1)
                        time.sleep(0.5)
                        pyautogui.click(*pos_extra1)

                        print(f"Clicked {pos_extra1}")
                        time.sleep(1)

                        pyautogui.click(*pos_extra2)
                        time.sleep(0.5)
                        pyautogui.click(*pos_extra2)

                        print(f"Clicked {pos_extra2}")
                        time.sleep(5)
                else:
                    pyautogui.click(*pos_extra1)
                    time.sleep(0.5)
                    pyautogui.click(*pos_extra1)

                    print(f"Clicked {pos_extra1}")
                    time.sleep(1)

                    pyautogui.click(*pos_extra2)
                    time.sleep(0.5)
                    pyautogui.click(*pos_extra2)

                    print(f"Clicked {pos_extra2}")
                    time.sleep(5)
                
            else:
                color_name = get_color_name(color_check_now)
                msg = f"⚠️ Miscrit rarity of {color_name}"
                print(msg)
                send_telegram_message(msg)
                exit_program = True
                sys.exit(0)

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
        # Convert RGB to hex
        hex_value = webcolors.rgb_to_hex(rgb_tuple)
        # Get the color name directly
        return webcolors.hex_to_name(hex_value)
    except ValueError:
        # If exact match not found, find the closest color
        return closest_color(rgb_tuple)

if __name__ == "__main__":
    print("Ready. Press  to start, ESC to quit.")
    # Start keyboard listener in a thread
    key_thread = threading.Thread(target=lambda: keyboard.Listener(on_press=on_key_press).run())
    key_thread.start()

    auto_clicker()

    sys.exit(0)