from argparse import ArgumentTypeError
import csv
from pathlib import Path

from nephele_pipeline_utils.parser import NepheleArgumentParser
from nephele_pipeline_utils.types import (
    boolean,
    directory,
    path,
    validate_path,
    file_extensions,
    mapping_file,
)

from config import pipeline_config
from enums import DataType


class ArgumentParser(NepheleArgumentParser):
    def validate_data(self):
        args = self.args
        if args.data_type in (DataType.ARTIC_PE, DataType.ARTIC_SE):
            if not args.primer_file_path:
                raise ArgumentTypeError(
                    "primer_file_path must be provided if data_type is ARTIC."
                )

        args.ref_db_path = Path(f"{args.ref_db_path}/SARS-CoV2.fa")

    def parse_args(self, **kwargs):
        args = super().parse_args(**kwargs)

        # discard extra metadata if exists
        fieldnames = list(args.samples[0].keys())
        allowed_fields = ["#SampleID", "ForwardFastqFile", "ReverseFastqFile"]

        fields_to_remove = set(fieldnames) - set(allowed_fields)
        if fields_to_remove:
            for field_to_remove in fields_to_remove:
                fieldnames.remove(field_to_remove)
            with open(args.mapping_file_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="\t")
                # Write the header
                writer.writeheader()
                # Write the data
                for sample in args.samples:
                    sample = sample.copy()
                    for field_to_remove in fields_to_remove:
                        del sample[field_to_remove]
                    writer.writerow(sample)

        return args

    def get_samples(self):
        super().get_samples()
        data_type = self.args.data_type

        sample_files = []
        if data_type == DataType.SGS_PE:
            sample_files = [
                "ForwardFastqFile_A",
                "ForwardFastqFile_B",
                "ReverseFastqFile_A",
                "ReverseFastqFile_B",
                "PrimerFile_A",
                "PrimerFile_B",
            ]
        elif data_type == DataType.SGS_SE:
            sample_files = [
                "ForwardFastqFile_A",
                "ForwardFastqFile_B",
                "PrimerFile_A",
                "PrimerFile_B",
            ]
        elif data_type == DataType.ARTIC_PE:
            sample_files = ["ForwardFastqFile", "ReverseFastqFile"]
        elif data_type == DataType.ARTIC_SE:
            sample_files = ["ForwardFastqFile"]

        for sample in self.args.samples:
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
        type=directory,
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
        type=mapping_file,
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
