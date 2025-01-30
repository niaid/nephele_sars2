from argparse import ArgumentTypeError
from pathlib import Path

from nephele_pipeline_utils.parser import NepheleArgumentParser
from nephele_pipeline_utils.types import (
    boolean,
    directory,
    path,
    validate_path,
    file_extensions,
)

from config import pipeline_config
from enums import DataType


class ArgumentParser(NepheleArgumentParser):
    @staticmethod
    def validate_data(args):
        if args.data_type in (DataType.ARTIC_PE, DataType.ARTIC_SE):
            if not args.primer_file_path:
                raise ArgumentTypeError(
                    "primer_file_path must be provided if data_type is ARTIC."
                )

    def get_samples(self, args):
        samples, sample_ids = super().get_samples(args)
        data_type = args.data_type

        sample_files = []
        if data_type == DataType.SGS_PE:
            sample_files = [
                "ForwardFastqFile_A",
                "ForwardFastqFile_B",
                "ReverseFastqFile_A",
                "ReverseFastqFile_B",
                "PrimerFile_A",
                "PrimerFile_B"
            ]
        elif data_type == DataType.SGS_SE:
            sample_files = [
                "ForwardFastqFile_A",
                "ForwardFastqFile_B",
                "PrimerFile_A",
                "PrimerFile_B"
            ]
        elif data_type == DataType.ARTIC_PE:
            sample_files = ["ForwardFastqFile", "ReverseFastqFile"]
        elif data_type == DataType.ARTIC_SE:
            sample_files = ["ForwardFastqFile"]

        for sample in samples:
            for sample_file in sample_files:
                if sample_file not in sample:
                    raise ArgumentTypeError(
                        f"{sample_file} must be present in the samples."
                    )

                file_type = "fa" if "Primer" in sample_file else "fastq"
                validate_path(file_extensions(file_type), sample[sample_file])


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--version",
        action="version",
        version=pipeline_config.version,
        help="show program's version number and exit",
    )
    parser.add_argument(
        "--data_type",
        type=str,
        required=True,
        choices=DataType.values(),
        help="data type",
    )
    parser.add_argument(
        "--ref_db_path",
        type=path("db"),
        required=True,
        help="ref db path.",
    )
    parser.add_argument(
        "--snpeff_db_path",
        type=directory,
        required=True,
        help="snpeff db path.",
    )
    parser.add_argument(
        "--get_bam_files",
        type=boolean,
        default=False,
        help="get bam files",
    )
    parser.add_argument(
        "--primer_file_path",
        type=path("db"),
        required=False,
        help="primer db file path. Required for ARTIC data type",
    )
    parser.add_argument(
        "--mapping_file_path",
        type=path("csv"),
        required=True,
        help="Input path to mapping file",
    )
    parser.add_argument(
        "--outputs_dir_path",
        type=directory,
        default=Path("/outputs"),
        help="Path to outputs directory",
    )
    return parser.parse_args()
