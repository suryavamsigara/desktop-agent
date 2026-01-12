from pydantic import BaseModel
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

