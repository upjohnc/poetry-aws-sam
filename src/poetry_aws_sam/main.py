from pathlib import Path

from poetry_aws_sam.aws import Config
from poetry_aws_sam.sam import AwsBuilder

ROOT_FILE = "pyproject.toml"


def find_root_dir() -> Path:
    present_dir = Path.cwd()

    # assume that 3 levels or less
    for _ in range(3):
        check = [i for i in present_dir.glob("*") if ROOT_FILE in i.name]

        if len(check) > 0:
            break
        present_dir = present_dir.parent

    return present_dir


def main_cli():
    config = Config(
        root_dir=find_root_dir(),
        groups={"with": "dev"},
        sam_exec="sam",
        requirements_format="requirements.txt",
        template_name="template.yml",
        without_hashes=True,
        with_credentials=True,
        without_urls=False,
    )

    _ = AwsBuilder(config).build_standard()


if __name__ == "__main__":
    main_cli()
