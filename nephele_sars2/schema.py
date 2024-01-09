# Schema for sars2 pipeline
import csv
from enum import Enum
from pathlib import Path
from typing import Optional

from nephele_pipeline_utils.io import PipelineInput
from nephele_pipeline_utils.utils import log
from pydantic import BaseModel, model_validator


class DataType(Enum):
    COVID19_PE = "COVID19_PE"
    COVID19_SE = "COVID19_SE"
    COVID19_PE_ARTIC = "COVID19_PE_ARTIC"
    COVID19_SE_ARTIC = "COVID19_SE_ARTIC"


class PipelineArguments(BaseModel):
    data_type: DataType
    primer_reference: Optional[Path] = None
    custom_primer: bool = False
    ref: Path
    snpeff_data_dir: Path
    get_bam_files: bool = False


class Sars2Pipeline(PipelineInput):
    pipeline_arguments: PipelineArguments

    @model_validator(mode="after")
    def validate_data(self):
        # Must have primer_reference if using ARTIC protocal
        data_type = self.pipeline_arguments.data_type
        primer_reference = self.pipeline_arguments.primer_reference
        if (
            data_type in [DataType.COVID19_PE_ARTIC, DataType.COVID19_SE_ARTIC]
            and not primer_reference
        ):
            raise ValueError("Missing primer_reference for ARTIC protocol")
        return self
