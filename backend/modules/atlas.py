class Atlas:

    def start(self):
        print("[ATLAS] Loading...")
        print("🗺️ Planner Ready")
        print()

    def plan(self, task):
        print("[ATLAS] Planning...")
        print(f"Intent : {task['intent']}")
        print(f"Target : {task['target']}")

        if task["intent"] == "OPEN_APP":
            return {
                "action": "LAUNCH_APP",
                "app": task["target"]
            }

        return {
            "action": "NO_OP",
            "app": task["target"],
            "reason": "Unknown command"
        }