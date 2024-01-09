from pathlib import Path

from nephele_pipeline_utils.config import SharedConfig


class TemplateConfig(SharedConfig):
    """
    A class for the pipeline configuration, which includes values read from the config.json file and other
    values defined below.
    """

    pipeline_base_dir: Path = Path("/pipeline")
    my_script_path: Path = pipeline_base_dir / "my_script.sh"


template_config = TemplateConfig.from_json(Path(__file__).parent / "config.json")
