import argparse
import csv
import os
import shlex
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

from config import pipeline_config
from nephele_pipeline_utils.exceptions import NephelePipelineError
from nephele_pipeline_utils.utils import log, read_json
from pydantic import ValidationError
from schema import (
    DataType,
    Sars2ARTICPipelinePE,
    Sars2ARTICPipelineSE,
    Sars2SGSPipelinePE,
    Sars2SGSPipelineSE,
)


def remove_intermediate_dirs(dname, dirs_to_keep):
    """remove_intermediate_dirs
    Removes dirs_to_keep from dname
    :param dname:
    :param dirs_to_keep:
    """
    output_dirs = os.listdir(dname)
    for output_dir in output_dirs:
        if output_dir in dirs_to_keep:
            continue
        dir_path = dname / output_dir
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)


def main(args):
    try:
        exit_status = 0
        report_outputs = False
        data = read_json(args.json_file_path)
        data_type = data.get("pipeline_arguments", {}).get("data_type", None)
        if data_type == DataType.SGS_PE:
            pipeline = Sars2SGSPipelinePE(**data)
        elif data_type == DataType.SGS_SE:
            pipeline = Sars2SGSPipelineSE(**data)
        elif data_type == DataType.ARTIC_PE:
            pipeline = Sars2ARTICPipelinePE(**data)
        elif data_type == DataType.ARTIC_SE:
            pipeline = Sars2ARTICPipelineSE(**data)
        else:
            raise ValidationError(f"Invalid data type: {data_type}")
        args = pipeline.pipeline_arguments
        outputs_dir_path = args.outputs_dir_path
        report_outputs = True
        # check Dependencies version
        try:
            log("Dependencies:")
            log("--------------------------------")
            dep = subprocess.run(
                shlex.split("./dependencies.sh"),
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            dep_stdout = dep.stdout.decode()
            log(dep_stdout)
            log("--------------------------------")
        except Exception as _:
            log("Warning: failed to check dependencies version.")
        # Select script
        if args.data_type == DataType.SGS_PE:
            script_name = pipeline_config.pe_script_path
        elif args.data_type == DataType.SGS_SE:
            script_name = pipeline_config.se_script_path
        elif args.data_type == DataType.ARTIC_PE:
            script_name = f"{pipeline_config.artic_script_path} --data_type PE"
        else:
            script_name = f"{pipeline_config.artic_script_path} --data_type SE"
        log(pipeline)
        # Generate mapping file
        mapping_file_path = outputs_dir_path / pipeline_config.mapping_file_name
        pipeline.generate_mapping_file(mapping_file_path, file_name_only=False)
        # Get ref_db_path params
        ref_db_path = args.ref_db_path
        # Get snpeff_db_path
        snpeff_db_path = args.snpeff_db_path
        # Command to execute the Nextflow pipeline
        command = (
            f"nextflow run -name {pipeline_config.nextflow_project_name} -c {pipeline_config.nextflow_config_path} -work-dir {pipeline_config.nextflow_work_dir} {script_name} "
            f"--outputs_dir {outputs_dir_path} --map_file {mapping_file_path} --ref_db_path {ref_db_path} --snpeff_db_path {snpeff_db_path}"
        )
        # For one-pool/Artic, we need to pass the primer filepath
        if args.data_type in [DataType.ARTIC_PE, DataType.ARTIC_SE]:
            command += f" --primer_file_path {args.primer_file_path}"
        log(command)
        # Run
        command_args = shlex.split(command)

        process = subprocess.run(command_args)

        if process.returncode == 1:
            # Nextflow somehow does not produce stderr, need the following to capture stderr
            stderr_capture_command = (
                f"nextflow log {pipeline_config.nextflow_project_name} -f stderr"
            )
            stderr_capture_result = subprocess.run(
                shlex.split(stderr_capture_command),
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            stderr_msg = stderr_capture_result.stdout.decode()
            raise NephelePipelineError(stderr_msg)
    except Exception:
        exit_status = 1
        error_msg = f"Pipeline Error:\n{traceback.format_exc()}"
        # explicitly writing to stderr
        print(error_msg, file=sys.stderr, flush=True)
    finally:
        try:
            log("Removing intermediate dirs...")
            dirs_to_keep = []
            if args.get_bam_files:
                dirs_to_keep.append("bam_files")
            if args.data_type in [DataType.SGS_PE, DataType.SGS_SE]:
                dirs_to_keep.extend(pipeline_config.sgs_dirs_to_keep)
            else:
                dirs_to_keep.extend(pipeline_config.artic_dirs_to_keep)
            remove_intermediate_dirs(outputs_dir_path, dirs_to_keep)
        except Exception as e:
            log(f"Warning: clean up step error: {str(e)}")

    # Report outputs
    if report_outputs:
        try:
            pipeline.report_outputs(
                Path(pipeline_config.outputs_template_file_name),
                outputs_dir_path / pipeline_config.outputs_report_file_name,
            )
        except Exception:
            log(f"Warning: error reporting outputs:\n {traceback.format_exc()}")

    if exit_status == 0:
        log("Pipeline completed")

    exit(exit_status)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        "--version",
        action="version",
        version=pipeline_config.version,
        help="show program's version number and exit",
    )
    PARSER.add_argument(
        "--json_file_path",
        type=Path,
        required=True,
        help=f"Input JSON file",
    )
    ARGS = PARSER.parse_args()
    main(ARGS)
