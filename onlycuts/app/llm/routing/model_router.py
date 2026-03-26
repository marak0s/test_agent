from onlycuts.app.config.model_routing import TASK_MODEL_DEFAULTS


class ModelRouter:
    def route(self, task: str) -> str:
        return TASK_MODEL_DEFAULTS[task]
