import os
import shlex
import shutil
import subprocess

from nephele_pipeline_utils.decorators import pre_post_step
from nephele_pipeline_utils.exceptions import NephelePipelineError
from nephele_pipeline_utils.utils import log

from config import pipeline_config
from enums import DataType
from parser import parse_args


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


def post_clean_up(args):
    try:
        log("Removing intermediate dirs...")
        dirs_to_keep = []
        if args.get_bam_files:
            dirs_to_keep.append("bam_files")
        if args.data_type in [DataType.SGS_PE, DataType.SGS_SE]:
            dirs_to_keep.extend(pipeline_config.sgs_dirs_to_keep)
        else:
            dirs_to_keep.extend(pipeline_config.artic_dirs_to_keep)
        remove_intermediate_dirs(args.outputs_dir_path, dirs_to_keep)
    except Exception as e:
        log(f"Warning: clean up step error: {str(e)}")


@pre_post_step(parse_args, pipeline_config, post_clean_up)
def main(args):
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
    if args.data_type == DataType.SGS_PE:
        script_name = pipeline_config.pe_script_path
    elif args.data_type == DataType.SGS_SE:
        script_name = pipeline_config.se_script_path
    elif args.data_type == DataType.ARTIC_PE:
        script_name = f"{pipeline_config.artic_script_path} --data_type PE"
    else:
        script_name = f"{pipeline_config.artic_script_path} --data_type SE"

    # Get ref_db_path params
    ref_db_path = args.ref_db_path
    # Get snpeff_db_path
    snpeff_db_path = args.snpeff_db_path
    # Command to execute the Nextflow pipeline
    command = (
        # 'CAPSULE_CACHE_DIR="$HOME/.nextflow_capsule_cache" '
        f"nextflow -Dcapsule.log=verbose -log /dev/stdout run -name {pipeline_config.nextflow_project_name} -c {pipeline_config.nextflow_config_path} -work-dir {pipeline_config.nextflow_work_dir} {script_name} "
        f"--outputs_dir {outputs_dir_path} --map_file {args.mapping_file_path} --ref_db_path {ref_db_path} --snpeff_db_path {snpeff_db_path}"
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


if __name__ == "__main__":
    main()
