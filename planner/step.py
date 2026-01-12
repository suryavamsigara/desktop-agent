from pydantic import BaseModel, model_validator
from typing import Union, Literal, Optional

from planner.action_schemas import (
    OpenAppParams,
    TypeParams,
    PressParams,
    ClickParams,
    WaitParams,
)

class Decision(BaseModel):
    action: Literal[
        "open_app",
        "type",
        "press",
        "click",
        "wait",
        "observe",
        "done"
    ]

    parameters: Optional[Union[
        OpenAppParams,
        TypeParams,
        PressParams,
        ClickParams,
        WaitParams,
        None,
    ]] = None
    thought: Optional[str] = None

    @model_validator(mode="after")
    def validate_action_params(self):
        if self.action == "open_app":
            if not self.parameters or not hasattr(self.parameters, "app_name"):
                raise ValueError("open_app requires parameters.app_name")

        if self.action == "type":
            if not self.parameters or not hasattr(self.parameters, "text"):
                raise ValueError("type requires parameters.text")

        if self.action == "press":
            if not self.parameters or not hasattr(self.parameters, "key"):
                raise ValueError("press requires parameters.key")

        if self.action == "click":
            if not isinstance(self.parameters, ClickParams):
                raise ValueError("click requires ClickParams with target")

        if self.action in ("observe", "done") and self.parameters is not None:
            raise ValueError(f"{self.action} must not have parameters")

        return self

