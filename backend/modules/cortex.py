import re


class Cortex:

    def understand(self, command):
        if not command or not isinstance(command, str):
            return {
                "intent": "UNKNOWN",
                "target": ""
            }

        normalized = " ".join(command.lower().strip().split())
        normalized = normalized.replace("’", "'")

        if normalized.startswith(("open ", "launch ")):
            target = normalized.replace("open", "", 1).replace("launch", "", 1).strip()
            if target.startswith("the "):
                target = target[4:]

            return {
                "intent": "OPEN_APP",
                "target": target
            }

        if normalized in ("click", "single click", "single-click"):
            return {"intent": "CLICK"}

        if normalized in ("double click", "double-click"):
            return {"intent": "DOUBLE_CLICK"}

        if normalized in ("right click", "right-click"):
            return {"intent": "RIGHT_CLICK"}

        move_match = re.match(r"^move mouse (up|down|left|right)$", normalized)
        if move_match:
            return {
                "intent": "MOVE_MOUSE",
                "direction": move_match.group(1)
            }

        move_to_match = re.match(r"^move mouse to\s*\(?\s*(\d+)\s*[, ]\s*(\d+)\s*\)?$", normalized)
        if move_to_match:
            return {
                "intent": "MOVE_MOUSE_TO",
                "x": int(move_to_match.group(1)),
                "y": int(move_to_match.group(2))
            }

        drag_match = re.match(r"^drag mouse(?: (up|down|left|right))?$", normalized)
        if drag_match:
            return {
                "intent": "DRAG_MOUSE",
                "direction": drag_match.group(1) or "right"
            }

        if normalized in ("scroll up", "scroll down"):
            return {
                "intent": "SCROLL",
                "direction": "up" if "up" in normalized else "down"
            }

        if normalized.startswith("type "):
            text = command.strip()[5:]
            return {
                "intent": "TYPE",
                "text": text
            }

        if normalized.startswith("press "):
            key_phrase = normalized[6:].strip().replace("control", "ctrl")
            key_phrase = re.sub(r"\s+", "", key_phrase)

            key_map = {
                "enter": "enter",
                "tab": "tab",
                "escape": "esc",
                "esc": "esc",
                "backspace": "backspace",
                "delete": "delete",
                "space": "space",
                "ctrl+c": "ctrl+c",
                "ctrlc": "ctrl+c",
                "ctrl+v": "ctrl+v",
                "ctrlv": "ctrl+v",
                "ctrl+s": "ctrl+s",
                "ctrls": "ctrl+s",
                "alt+tab": "alt+tab",
                "alttab": "alt+tab"
            }
            if key_phrase in key_map:
                return {
                    "intent": "PRESS_KEY",
                    "key": key_map[key_phrase]
                }

        return {
            "intent": "UNKNOWN",
            "target": normalized
        }