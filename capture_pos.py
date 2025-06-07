from pynput import mouse, keyboard
from PIL import ImageGrab
import threading

start_listening = False
mouse_listener = None
keyboard_listener = None

def on_key_press(key):
    global start_listening, mouse_listener, keyboard_listener
    try:
        if key.char == '`' and not start_listening:
            print("` key pressed. Now listening for mouse clicks...")
            start_listening = True
    except AttributeError:
        if key == keyboard.Key.esc:
            print("ESC pressed. Exiting program...")
            if mouse_listener:
                mouse_listener.stop()
            if keyboard_listener:
                keyboard_listener.stop()

def on_click(x, y, button, pressed):
    if pressed and start_listening:
        img = ImageGrab.grab().load()
        color = img[x, y]
        print(f"Clicked at ({x}, {y}) - Color: RGB{color}")

def start_keyboard_listener():
    global keyboard_listener
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    keyboard_listener.start()
    keyboard_listener.join()

def start_mouse_listener():
    global mouse_listener
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    mouse_listener.join()

# Run both listeners
print("Press ` to start logging mouse clicks.")
print("Press ESC at any time to quit.")

# Run keyboard listener in a thread so it doesn’t block mouse listener
keyboard_thread = threading.Thread(target=start_keyboard_listener)
keyboard_thread.start()

# Run mouse listener in the main thread
start_mouse_listener()

keyboard_thread.join()
