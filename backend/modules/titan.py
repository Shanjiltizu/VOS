import platform
import subprocess


class Titan:

    def start(self):
        print("[TITAN] Loading...")
        print("🚀 Execution Engine Ready")
        print()

    def execute(self, plan):
        if plan.get("action") != "LAUNCH_APP":
            return {
                "status": "FAILED",
                "message": "I did not receive a valid execution plan."
            }

        app = plan.get("app", "").lower()
        if "chrome" in app:
            return self._launch_chrome()

        return {
            "status": "FAILED",
            "message": f"I cannot launch '{app}'. Only Chrome is supported in this sprint."
        }

    def _launch_chrome(self):
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["cmd", "/c", "start", "", "chrome"])
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", "Google Chrome"])
            else:
                subprocess.Popen(["google-chrome"])

            return {
                "status": "SUCCESS",
                "message": "Chrome is now open."
            }
        except FileNotFoundError:
            return {
                "status": "FAILED",
                "message": "Google Chrome could not be found on this machine."
            }
        except Exception as error:
            return {
                "status": "FAILED",
                "message": f"Failed to launch Chrome: {error}"
            }