class Atlas:

    APP_LOOKUP = {
        "chrome": ("chrome", "Chrome"),
        "google chrome": ("chrome", "Chrome"),
        "notepad": ("notepad", "Notepad"),
        "calculator": ("calculator", "Calculator"),
        "file explorer": ("explorer", "File Explorer"),
        "explorer": ("explorer", "File Explorer"),
        "settings": ("settings", "Settings"),
        "vs code": ("vscode", "VS Code"),
        "vscode": ("vscode", "VS Code"),
        "code": ("vscode", "VS Code"),
        "edge": ("edge", "Edge"),
        "firefox": ("firefox", "Firefox"),
    }

    def start(self):
        print("[ATLAS] Loading...")
        print("🗺️ Planner Ready")
        print()

    def plan(self, task):
        if not isinstance(task, dict):
            return {"action": "NO_OP", "reason": "Invalid task"}

        print("[ATLAS] Planning...")
        print(f"Intent : {task.get('intent', 'UNKNOWN')}")
        print(f"Target : {task.get('target', '')}")

        intent = task.get("intent", "UNKNOWN")

        if intent == "OPEN_APP":
            target = str(task.get("target", "")).lower().strip()
            target = target.replace("the ", "")

            for phrase, (app_key, app_label) in self.APP_LOOKUP.items():
                if phrase in target:
                    return {
                        "action": "LAUNCH_APP",
                        "app": app_key,
                        "label": app_label
                    }

            return {
                "action": "NO_OP",
                "app": target,
                "reason": "Unsupported application"
            }

        if intent == "CLICK":
            return {"action": "CLICK", "button": "left"}

        if intent == "DOUBLE_CLICK":
            return {"action": "DOUBLE_CLICK"}

        if intent == "RIGHT_CLICK":
            return {"action": "RIGHT_CLICK"}

        if intent == "MOVE_MOUSE":
            return {"action": "MOVE_MOUSE", "direction": task.get("direction", "right"), "distance": 100}

        if intent == "MOVE_MOUSE_TO":
            return {"action": "MOVE_MOUSE_TO", "x": task.get("x"), "y": task.get("y")}

        if intent == "DRAG_MOUSE":
            return {"action": "DRAG_MOUSE", "direction": task.get("direction", "right"), "distance": 150}

        if intent == "SCROLL":
            amount = 200 if task.get("direction") == "up" else -200
            return {"action": "SCROLL", "amount": amount}

        if intent == "TYPE":
            return {"action": "TYPE", "text": task.get("text", "")}

        if intent == "PRESS_KEY":
            return {"action": "PRESS_KEY", "key": task.get("key", "")}

        return {
            "action": "NO_OP",
            "app": task.get("target", ""),
            "reason": "Unknown command"
        }