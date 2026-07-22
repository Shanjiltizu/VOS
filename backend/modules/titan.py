import platform
import subprocess


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