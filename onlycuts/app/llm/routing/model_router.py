from onlycuts.app.config.model_routing import TASK_MODEL_DEFAULTS


class ModelRouter:
    def route(self, task: str) -> dict:
        return {
            "model": TASK_MODEL_DEFAULTS[task],
            "tools": TASK_TOOL_DEFAULTS.get(task, []),
        }