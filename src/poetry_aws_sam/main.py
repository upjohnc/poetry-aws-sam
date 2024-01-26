from pathlib import Path

from poetry_aws_sam.aws import Config
from poetry_aws_sam.sam import AwsBuilder


def main_cli():
    config = Config(
        root_dir=Path.cwd(),
        sam_exec="sam",
        template_name="template.yml",
    )

    _ = AwsBuilder(config).build_standard()
