from pathlib import Path
from typing import List

from nephele_pipeline_utils.config import SharedConfig


class Sars2Config(SharedConfig):
    nextflow_project_name: str
    nextflow_work_dir: Path
    mapping_file_name: Path
    pe_script_path: Path
    se_script_path: Path
    artic_script_path: Path
    nextflow_config_path: Path
    sgs_dirs_to_keep: List[str]
    artic_dirs_to_keep: List[str]


pipeline_config = Sars2Config.from_json("./config.json")
