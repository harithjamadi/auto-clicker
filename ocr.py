import cv2
import numpy as np
from PIL import ImageGrab
import easyocr
from pynput import keyboard
import pygetwindow as gw
import pyautogui

# Initialize OCR reader
reader = easyocr.Reader(['en'])
roi = None  # (x1, y1, x2, y2)

# ---------- Step 1: Get Application Window ----------
def get_window_bbox(app_name):
    matches = [w for w in gw.getWindowsWithTitle(app_name) if w.visible and w.width > 0 and w.height > 0]
    if not matches:
        print(f"No visible window found with name containing '{app_name}'.")
        return None
    win = matches[0]
    print(f"Found window: '{win.title}' at ({win.left}, {win.top}, {win.width}, {win.height})")
    return (win.left, win.top, win.left + win.width, win.top + win.height)

# ---------- Step 2: Select ROI within the app window ----------
def select_roi_in_window(window_bbox):
    print("Please select ROI inside the application window. Press ENTER or SPACE to confirm.")
    img = np.array(ImageGrab.grab(bbox=window_bbox))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    rel_roi = cv2.selectROI("Select Region", img, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()

    if rel_roi[2] == 0 or rel_roi[3] == 0:
        print("ROI selection cancelled.")
        return None
    
    x_offset, y_offset = window_bbox[0], window_bbox[1]
    x1, y1, w, h = rel_roi
    return (x1 + x_offset, y1 + y_offset, x1 + x_offset + w, y1 + y_offset + h)

# ---------- Step 3: Key Press Listener ----------
def on_press(key):
    global roi
    try:
        if key.char == '`':
            if roi is None:
                print("No ROI set. Please define it first.")
                return

            img = ImageGrab.grab(bbox=roi)
            img_np = np.array(img)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            cv2.imshow("Captured ROI", img_bgr)
            cv2.waitKey(500)
            cv2.destroyAllWindows()

            results = reader.readtext(img_np)
            print("OCR Results:")
            if results:
                for (bbox, text, prob) in results:
                    print(f"Detected: '{text}' (Confidence: {prob:.2f}) at {bbox}")
            else:
                print("No text detected.")
    except AttributeError:
        if key == keyboard.Key.esc:
            print("Exiting program.")
            return False

# ---------- Step 4: Main ----------
if __name__ == "__main__":
    app_title = "Miscrits"
    win_bbox = get_window_bbox(app_title)

    if win_bbox:
        roi = select_roi_in_window(win_bbox)

        if roi:
            print(f"ROI set to: {roi}")
            print("Press ` to capture the region and run OCR.")
            print("Press ESC to exit.")
            with keyboard.Listener(on_press=on_press) as listener:
                listener.join()
