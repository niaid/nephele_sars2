# Schema for sars2 pipeline
import csv
from enum import Enum
from pathlib import Path
from typing import List, Optional

from nephele_pipeline_utils.io import (
    Pipeline,
    PipelineArguments,
    PipelinePE,
    PipelineSE,
    Sample,
)
from nephele_pipeline_utils.utils import log
from pydantic import BaseModel, ConfigDict, FilePath, model_validator


class DataType(str, Enum):
    SGS_PE = "SGS_PE"
    SGS_SE = "SGS_SE"
    ARTIC_PE = "ARTIC_PE"
    ARTIC_SE = "ARTIC_SE"


class SampleSgsSE(Sample):
    forward_fastq_file_a_path: FilePath
    forward_fastq_file_b_path: FilePath
    primer_file_a_path: FilePath
    primer_file_b_path: FilePath


class SampleSgsPE(SampleSgsSE):
    reverse_fastq_file_a_path: FilePath
    reverse_fastq_file_b_path: FilePath


class PipelineArgumentsSGS(PipelineArguments):
    model_config = ConfigDict(use_enum_values=True)
    data_type: DataType
    ref_db_path: Path
    snpeff_db_path: Path
    get_bam_files: bool = False


class PipelineArgumentsARTIC(PipelineArgumentsSGS):
    primer_file_path: FilePath


class Sars2ARTICPipelineSE(PipelineSE):
    pipeline_arguments: PipelineArgumentsARTIC


class Sars2ARTICPipelinePE(PipelinePE):
    pipeline_arguments: PipelineArgumentsARTIC


class Sars2SGSPipelineSE(Pipeline):
    samples: List[SampleSgsSE]
    pipeline_arguments: PipelineArgumentsSGS


class Sars2SGSPipelinePE(Pipeline):
    samples: List[SampleSgsPE]
    pipeline_arguments: PipelineArgumentsSGS
