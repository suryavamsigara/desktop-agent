from pydantic import BaseModel
from typing import Union, Literal

from planner.action_schemas import (
    OpenAppParams,
    TypeParams,
    PressParams,
    ClickParams,
    WaitParams,
)

class Step(BaseModel):
    action: Literal[
        "open_app",
        "type",
        "press",
        "click",
        "wait",
        "observe",
    ]

    parameters: Union[
        OpenAppParams,
        TypeParams,
        PressParams,
        ClickParams,
        WaitParams,
        None,
    ] = None

