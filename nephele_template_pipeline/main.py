#!/usr/bin/env python3

import argparse
from pathlib import Path

from config import template_config as config
from nephele_pipeline_utils.utils import exec_cmnd, log
from schema import TemplatePipelineInput


def main(args):
    # Parse and validate pipeline input file that indicates
    # input files and pipeline arguments
    pipeline_input = TemplatePipelineInput.from_json(args.json_file_path)
    log(f"Pipeline input: {pipeline_input}")

    # Study the PipelineInput class API in the documentation
    # to see what information is available

    # Implement pipeline logic below. If your pipeline calls a shell script,
    # consider using exec_cmnd() function from nephele_pipeline_utils.utils module
    exec_cmnd(f"{config.my_script_path} arg1 arg2")


if __name__ == "__main__":
    # Parse command-line arguments, the only argument is the input JSON file that should
    # be sufficient and necessary to run the pipeline
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        "--version",
        action="version",
        version=config.version,
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
