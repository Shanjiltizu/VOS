import os
import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path

try:
    import mss
    import PIL.Image
except ImportError:  # pragma: no cover - optional dependency fallback
    mss = None
    PIL = None

try:
    import cv2
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency fallback
    cv2 = None
    np = None

try:
    from easyocr import Reader
except ImportError:  # pragma: no cover - optional dependency fallback
    Reader = None


class Titan:

    def start(self):
        print("[TITAN] Loading...")
        print("🚀 Execution Engine Ready")
        print()

    def execute(self, plan):
        if not isinstance(plan, dict):
            return {
                "status": "FAILED",
                "message": "I did not receive a valid execution plan."
            }

        action = plan.get("action")
        if not action:
            return {
                "status": "FAILED",
                "message": "I did not receive a valid execution plan."
            }

        if action == "LAUNCH_APP":
            return self._launch_app(plan)

        if action in {"CAPTURE_SCREEN", "CAPTURE_ACTIVE_WINDOW", "DESCRIBE_SCREEN", "GET_SCREEN_INFO"}:
            return self._handle_screen_action(plan)

        if action in {"OCR_SCREEN", "OCR_WINDOW", "OCR_IMAGE"}:
            return self._handle_ocr_action(plan)

        automation_map = {
            "CLICK": self._action_click,
            "DOUBLE_CLICK": self._action_double_click,
            "RIGHT_CLICK": self._action_right_click,
            "MOVE_MOUSE": self._action_move_mouse,
            "MOVE_MOUSE_TO": self._action_move_mouse_to,
            "DRAG_MOUSE": self._action_drag_mouse,
            "SCROLL": self._action_scroll,
            "TYPE": self._action_type,
            "PRESS_KEY": self._action_press_key,
        }

        action_handler = automation_map.get(action)
        if not action_handler:
            return {
                "status": "FAILED",
                "message": f"Unsupported action: {action}."
            }

        pyautogui = self._load_pyautogui()
        if pyautogui is None:
            return {
                "status": "FAILED",
                "message": "Desktop automation dependency pyautogui is not installed."
            }

        try:
            return action_handler(plan, pyautogui)
        except Exception as error:
            return {
                "status": "FAILED",
                "message": f"Automation failed: {error}"
            }

    def _launch_app(self, plan):
        app = str(plan.get("app", "")).lower()
        label = plan.get("label", app.title())

        launch_map = {
            "chrome": self._launch_chrome,
            "notepad": self._launch_notepad,
            "calculator": self._launch_calculator,
            "explorer": self._launch_explorer,
            "settings": self._launch_settings,
            "vscode": self._launch_vscode,
            "edge": self._launch_edge,
            "firefox": self._launch_firefox,
        }

        launcher = launch_map.get(app)
        if not launcher:
            return {
                "status": "FAILED",
                "message": f"I cannot launch '{label}'."
            }

        result = launcher()
        if result["status"] == "SUCCESS":
            result["message"] = f"Opening {label}."
        return result

    def _load_pyautogui(self):
        try:
            import pyautogui
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.05
            return pyautogui
        except ImportError:
            return None
        except Exception:
            return None

    def _handle_screen_action(self, plan):
        action = plan.get("action")
        screenshots_dir = Path(__file__).resolve().parents[1] / "assets" / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        if action == "GET_SCREEN_INFO":
            metadata = self._collect_screen_metadata()
            return {"status": "SUCCESS", "message": self._format_screen_info(metadata), "metadata": metadata}

        if action == "DESCRIBE_SCREEN":
            metadata = self._collect_screen_metadata()
            return {
                "status": "SUCCESS",
                "message": f"Screen size is {metadata['width']} by {metadata['height']}.",
                "metadata": metadata,
            }

        if action == "CAPTURE_SCREEN":
            captured = self._capture_screenshot(screenshots_dir, window=False)
            if captured["status"] != "SUCCESS":
                return captured
            return {
                "status": "SUCCESS",
                "message": "Screenshot captured.",
                "metadata": captured["metadata"],
            }

        if action == "CAPTURE_ACTIVE_WINDOW":
            captured = self._capture_screenshot(screenshots_dir, window=True)
            if captured["status"] != "SUCCESS":
                return captured
            return {
                "status": "SUCCESS",
                "message": "Active window captured.",
                "metadata": captured["metadata"],
            }

        return {"status": "FAILED", "message": f"Unsupported screen action: {action}."}

    def _collect_screen_metadata(self):
        try:
            import pygetwindow as pw
        except ImportError:  # pragma: no cover - optional dependency fallback
            pw = None

        title = ""
        if pw is not None:
            try:
                active_window = pw.getActiveWindow()
                if active_window is not None:
                    title = active_window.title
            except Exception:
                title = ""

        width = 0
        height = 0
        try:
            if mss is not None:
                with mss.mss() as sct:
                    monitor = sct.monitors[0]
                    width = monitor.get("width", 0)
                    height = monitor.get("height", 0)
        except Exception:
            width = 0
            height = 0

        return {
            "width": width,
            "height": height,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "active_window_title": title,
            "platform": platform.system(),
            "screenshot_location": str(Path(__file__).resolve().parents[1] / "assets" / "screenshots"),
        }

    def _capture_screenshot(self, screenshots_dir, window=False):
        if mss is None or PIL is None:
            return {"status": "FAILED", "message": "Screenshot dependencies are not installed."}

        try:
            with mss.mss() as sct:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                output_path = screenshots_dir / filename
                if window:
                    try:
                        import pygetwindow as pw
                    except ImportError:  # pragma: no cover - optional dependency fallback
                        return {"status": "FAILED", "message": "Window capture requires pygetwindow."}

                    try:
                        active_window = pw.getActiveWindow()
                        if active_window is None:
                            return {"status": "FAILED", "message": "No active window detected."}
                        left, top, right, bottom = active_window.left, active_window.top, active_window.right, active_window.bottom
                        if left < 0 or top < 0 or right <= left or bottom <= top:
                            return {"status": "FAILED", "message": "The active window could not be captured."}
                        sct_img = sct.grab({"left": left, "top": top, "width": right - left, "height": bottom - top})
                    except Exception as error:
                        return {"status": "FAILED", "message": f"Failed to capture active window: {error}"}
                else:
                    sct_img = sct.grab(sct.monitors[0])

                image = PIL.Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                image.save(output_path)

                metadata = self._collect_screen_metadata()
                metadata["screenshot_location"] = str(output_path)
                return {"status": "SUCCESS", "metadata": metadata}
        except Exception as error:
            return {"status": "FAILED", "message": f"Screenshot capture failed: {error}"}

    def _format_screen_info(self, metadata):
        size_text = f"{metadata.get('width', 0)} by {metadata.get('height', 0)}"
        title = metadata.get("active_window_title") or "unknown"
        return f"Screen size is {size_text}. Active window is {title}."

    def _handle_ocr_action(self, plan):
        action = plan.get("action")
        image_path = plan.get("image_path") or self._resolve_ocr_image_path(action)

        if not image_path:
            return {
                "status": "FAILED",
                "message": "No screenshot is available to read. Capture a screenshot first."
            }

        image_path = Path(image_path)
        if not image_path.exists():
            return {
                "status": "FAILED",
                "message": f"The image path does not exist: {image_path}"
            }

        try:
            started_at = time.perf_counter()
            raw_text, confidence = self._ocr_image(image_path)
            processing_time = round(time.perf_counter() - started_at, 3)
        except Exception as error:
            return {
                "status": "FAILED",
                "message": f"OCR failed: {error}"
            }

        if not raw_text or not str(raw_text).strip():
            return {
                "status": "SUCCESS",
                "message": "No readable text detected.",
                "raw_text": "",
                "confidence": 0.0,
                "processing_time": processing_time,
                "image_path": str(image_path),
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }

        display_text = self._summarize_for_speech(raw_text)
        return {
            "status": "SUCCESS",
            "message": display_text,
            "raw_text": raw_text,
            "confidence": confidence,
            "processing_time": processing_time,
            "image_path": str(image_path),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    def _resolve_ocr_image_path(self, action):
        screenshots_dir = Path(__file__).resolve().parents[1] / "assets" / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        candidates = []
        if screenshots_dir.exists():
            for file_path in screenshots_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}:
                    candidates.append(file_path)

        if not candidates:
            return None

        candidates.sort(key=lambda item: item.stat().st_mtime, reverse=True)
        return str(candidates[0])

    def _ocr_image(self, image_path):
        if cv2 is None or np is None or Reader is None:
            raise RuntimeError("OCR dependencies are not installed.")

        if not hasattr(self, "_ocr_reader"):
            self._ocr_reader = Reader(["en"], gpu=False)

        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError("The image could not be read.")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results = self._ocr_reader.readtext(thresh)

        if not results:
            return "", 0.0

        text_chunks = []
        confidences = []
        for _, text, confidence in results:
            if text and text.strip():
                text_chunks.append(text.strip())
                confidences.append(float(confidence))

        cleaned_text = "\n".join(text_chunks)
        confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0.0
        return cleaned_text, confidence

    def _summarize_for_speech(self, text, max_chars=500):
        if len(text) <= max_chars:
            return text

        preview = text[:max_chars].rstrip()
        return f"{preview}..."

    def _action_click(self, plan, pyautogui):
        pyautogui.click()
        return {"status": "SUCCESS", "message": "Click performed."}

    def _action_double_click(self, plan, pyautogui):
        pyautogui.doubleClick()
        return {"status": "SUCCESS", "message": "Double click performed."}

    def _action_right_click(self, plan, pyautogui):
        pyautogui.click(button="right")
        return {"status": "SUCCESS", "message": "Right click performed."}

    def _action_move_mouse(self, plan, pyautogui):
        direction = plan.get("direction")
        distance = plan.get("distance", 100)
        offsets = {
            "up": (0, -distance),
            "down": (0, distance),
            "left": (-distance, 0),
            "right": (distance, 0),
        }
        if direction not in offsets:
            return {"status": "FAILED", "message": f"Unsupported move direction: {direction}."}

        dx, dy = offsets[direction]
        pyautogui.moveRel(dx, dy, duration=0.1)
        return {"status": "SUCCESS", "message": f"Moved mouse {direction}."}

    def _action_move_mouse_to(self, plan, pyautogui):
        x = plan.get("x")
        y = plan.get("y")
        if x is None or y is None:
            return {"status": "FAILED", "message": "Move to coordinates are missing."}

        pyautogui.moveTo(x, y, duration=0.1)
        return {"status": "SUCCESS", "message": f"Moved mouse to {x}, {y}."}

    def _action_drag_mouse(self, plan, pyautogui):
        direction = plan.get("direction", "right")
        distance = plan.get("distance", 150)
        offsets = {
            "up": (0, -distance),
            "down": (0, distance),
            "left": (-distance, 0),
            "right": (distance, 0),
        }
        if direction not in offsets:
            return {"status": "FAILED", "message": f"Unsupported drag direction: {direction}."}

        dx, dy = offsets[direction]
        pyautogui.dragRel(dx, dy, duration=0.2, button="left")
        return {"status": "SUCCESS", "message": f"Dragged mouse {direction}."}

    def _action_scroll(self, plan, pyautogui):
        amount = plan.get("amount", 0)
        if amount == 0:
            return {"status": "FAILED", "message": "Scroll amount is missing."}

        pyautogui.scroll(amount)
        direction = "up" if amount > 0 else "down"
        return {"status": "SUCCESS", "message": f"Scrolled {direction}."}

    def _action_type(self, plan, pyautogui):
        text = plan.get("text", "")
        if not text:
            return {"status": "FAILED", "message": "No text provided to type."}

        pyautogui.write(text, interval=0.05)
        return {"status": "SUCCESS", "message": f"Typed {text}."}

    def _action_press_key(self, plan, pyautogui):
        key = plan.get("key")
        if not key:
            return {"status": "FAILED", "message": "No key provided to press."}

        if "+" in key:
            keys = key.split("+")
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(key)

        readable_key = key.replace("+", " + ").upper()
        return {"status": "SUCCESS", "message": f"Pressed {readable_key}."}

    def _launch_chrome(self):
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["cmd", "/c", "start", "", "chrome"])
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", "Google Chrome"])
            else:
                subprocess.Popen(["google-chrome"])

            return {"status": "SUCCESS", "message": ""}
        except FileNotFoundError:
            return {"status": "FAILED", "message": "Google Chrome could not be found on this machine."}
        except Exception as error:
            return {"status": "FAILED", "message": f"Failed to launch Chrome: {error}"}

    def _launch_notepad(self):
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["notepad"])
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", "TextEdit"])
            else:
                subprocess.Popen(["gedit"])

            return {"status": "SUCCESS", "message": ""}
        except FileNotFoundError:
            return {"status": "FAILED", "message": "Notepad or text editor could not be found on this machine."}
        except Exception as error:
            return {"status": "FAILED", "message": f"Failed to launch Notepad: {error}"}

    def _launch_calculator(self):
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["calc"])
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", "Calculator"])
            else:
                subprocess.Popen(["gnome-calculator"])

            return {"status": "SUCCESS", "message": ""}
        except FileNotFoundError:
            return {"status": "FAILED", "message": "Calculator could not be found on this machine."}
        except Exception as error:
            return {"status": "FAILED", "message": f"Failed to launch Calculator: {error}"}

    def _launch_explorer(self):
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["explorer"])
            elif system == "Darwin":
                subprocess.Popen(["open", "."])
            else:
                subprocess.Popen(["xdg-open", "."])

            return {"status": "SUCCESS", "message": ""}
        except FileNotFoundError:
            return {"status": "FAILED", "message": "File Explorer could not be opened on this machine."}
        except Exception as error:
            return {"status": "FAILED", "message": f"Failed to open File Explorer: {error}"}

    def _launch_settings(self):
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["cmd", "/c", "start", "", "ms-settings:"])
            elif system == "Darwin":
                subprocess.Popen(["open", "/System/Applications/System Settings.app"])
            else:
                subprocess.Popen(["gnome-control-center"])

            return {"status": "SUCCESS", "message": ""}
        except FileNotFoundError:
            return {"status": "FAILED", "message": "Settings could not be opened on this machine."}
        except Exception as error:
            return {"status": "FAILED", "message": f"Failed to open Settings: {error}"}

    def _launch_vscode(self):
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["cmd", "/c", "start", "", "code"])
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", "Visual Studio Code"])
            else:
                subprocess.Popen(["code"])

            return {"status": "SUCCESS", "message": ""}
        except FileNotFoundError:
            return {"status": "FAILED", "message": "VS Code could not be found on this machine."}
        except Exception as error:
            return {"status": "FAILED", "message": f"Failed to launch VS Code: {error}"}

    def _launch_edge(self):
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["cmd", "/c", "start", "", "msedge"])
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", "Microsoft Edge"])
            else:
                subprocess.Popen(["microsoft-edge"])

            return {"status": "SUCCESS", "message": ""}
        except FileNotFoundError:
            return {"status": "FAILED", "message": "Microsoft Edge could not be found on this machine."}
        except Exception as error:
            return {"status": "FAILED", "message": f"Failed to launch Edge: {error}"}

    def _launch_firefox(self):
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["cmd", "/c", "start", "", "firefox"])
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", "Firefox"])
            else:
                subprocess.Popen(["firefox"])

            return {"status": "SUCCESS", "message": ""}
        except FileNotFoundError:
            return {"status": "FAILED", "message": "Firefox could not be found on this machine."}
        except Exception as error:
            return {"status": "FAILED", "message": f"Failed to launch Firefox: {error}"}