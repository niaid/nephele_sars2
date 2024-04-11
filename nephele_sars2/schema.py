# Schema for sars2 pipeline
from typing import List, Optional

from nephele_pipeline_utils.io import (
    Pipeline,
    PipelineArguments,
    PipelinePE,
    PipelineSE,
    Sample,
    StrEnum,
)
from pydantic import DirectoryPath, FilePath


class DataType(StrEnum):
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
    data_type: DataType
    ref_db_path: FilePath
    snpeff_db_path: DirectoryPath
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
