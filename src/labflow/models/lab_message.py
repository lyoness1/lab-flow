from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: Literal["potassium", "sodium", "glucose"]
    value: float
    unit: str = Field(min_length=1)


class LabMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["lab-message-v0"]
    message_id: str = Field(min_length=1)
    patient_ref: str = Field(min_length=1)
    observations: list[Observation] = Field(min_length=1)


class LabMessageCreateResponse(BaseModel):
    workflow_run_id: str
    message_id: str
    state: Literal["RECEIVED"] = "RECEIVED"
