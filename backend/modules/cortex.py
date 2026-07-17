class Cortex:

    def understand(self, command):
        if not command:
            return {
                "intent": "UNKNOWN",
                "target": ""
            }

        normalized = command.lower().strip()

        if "open" in normalized or "launch" in normalized:
            target = normalized.replace("open", "").replace("launch", "").strip()
            if target.startswith("the "):
                target = target[4:]

            return {
                "intent": "OPEN_APP",
                "target": target
            }

        return {
            "intent": "UNKNOWN",
            "target": normalized
        }