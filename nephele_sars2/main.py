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
        data = read_json(args.json_file_path)
        data_type = data.get("pipeline_arguments", {}).get("data_type", None)
        if data_type == DataType.COVID19_PE:
            pipeline = Sars2SGSPipelinePE(**data)
        elif data_type == DataType.COVID19_SE:
            pipeline = Sars2SGSPipelineSE(**data)
        elif data_type == DataType.COVID19_PE_ARTIC:
            pipeline = Sars2ARTICPipelinePE(**data)
        elif data_type == DataType.COVID19_SE_ARTIC:
            pipeline = Sars2ARTICPipelineSE(**data)
        else:
            raise ValueError(f"Invalid data type: {data_type}")
        log(f"Pipeline input: {pipeline}")
        # pipeline = Sars2Pipeline.from_json(args.json_file_path)
        args = pipeline.pipeline_arguments
        outputs_dir_path = args.outputs_dir_path
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
        if args.data_type == DataType.COVID19_PE:
            script_name = pipeline_config.pe_script_path
        elif args.data_type == DataType.COVID19_SE:
            script_name = pipeline_config.se_script_path
        elif args.data_type == DataType.COVID19_PE_ARTIC:
            script_name = f"{pipeline_config.artic_script_path} --data_type PE"
        else:
            script_name = f"{pipeline_config.artic_script_path} --data_type SE"
        log(pipeline)
        # Generate mapping file
        mapping_file_path = outputs_dir_path / pipeline_config.mapping_file_name
        pipeline.generate_mapping_file(mapping_file_path, file_name_only=False)
        # Get ref params
        ref = args.ref
        # Get snpeff_data_dir
        snpeff_data_dir = args.snpeff_data_dir
        # Command to execute the Nextflow pipeline
        command = (
            f"nextflow run -name {pipeline_config.nextflow_project_name} -c {pipeline_config.nextflow_config_path} -work-dir {pipeline_config.nextflow_work_dir} {script_name} "
            f"--outputs_dir {outputs_dir_path} --map_file {mapping_file_path} --ref {ref} --snpeff_data_dir {snpeff_data_dir}"
        )
        # For one-pool/Artic, we need to pass the primer filepath
        if args.data_type in [DataType.COVID19_PE_ARTIC, DataType.COVID19_SE_ARTIC]:
            # if args.custom_primer is True:
            #     primer_file_path = (
            #         pipeline_config.inputs_dir_path / args.primer_reference
            #     )
            # else:
            #     primer_file_path = pipeline_config.db_dir_path / args.primer_reference
            command += f" --primer_file {args.primer_reference}"
        log(command)
        # Run
        command_args = shlex.split(command)
        # Only run
        # result = subprocess.run(
        #     command_args, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        # )
        # log(result.stdout.decode())

        # # Run and flush stdout while waiting for the process to be finished
        # process = subprocess.Popen(
        #     command_args,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     text=True,
        #     bufsize=1,
        #     universal_newlines=True,
        # )
        # # Loop to continuously read and flush stdout/stderr
        # while True:
        #     # Read a line from stdout
        #     stdout_line = process.stdout.readline()
        #     if stdout_line:
        #         # Print the line and flush the output
        #         log(stdout_line)
        #     else:
        #         break  # No more output from stdout
        # # Wait for the subprocess to complete
        # process.wait()

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
    else:
        log("Pipeline completed")
    finally:
        try:
            log("Removing intermediate dirs...")
            dirs_to_keep = []
            if args.get_bam_files:
                dirs_to_keep.append("bam_files")
            if args.data_type in [DataType.COVID19_PE, DataType.COVID19_SE]:
                dirs_to_keep.extend(pipeline_config.sgs_dirs_to_keep)
            else:
                dirs_to_keep.extend(pipeline_config.artic_dirs_to_keep)
            remove_intermediate_dirs(outputs_dir_path, dirs_to_keep)
        except Exception as e:
            log(f"Warning: clean up step error: {str(e)}")
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
