# Schema for template pipeline

from enum import Enum
from typing import Optional

from nephele_pipeline_utils.io import PipelineInput
from psutil import virtual_memory
from pydantic import BaseModel, Field, validator


class DataType(Enum):
    SE = "se"
    PE = "pe"


class PipelineArguments(BaseModel):
    data_type: DataType
    threads: Optional[int] = Field(10, ge=1)  # use inline validator whenever possible
    mem_gb: Optional[int] = None

    # implement custom validator when the validation logic is more complex
    @validator("mem_gb")
    def check_mem_gb(cls, v, values):
        if v is None:
            v = int(virtual_memory().total / 1e9)
        if v < 1:
            raise ValueError("mem_gb must be >= 1")
        return v


class TemplatePipelineInput(PipelineInput):
    pipeline_arguments: PipelineArguments
