from pathlib import Path

import click

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


@click.command()
@click.option("--without-hashes", is_flag=True, default=False)
@click.option("--with_credentials", is_flag=True, default=False)
@click.option("--without_urls", is_flag=True, default=False)
@click.option("--requirements_format", default="requirements.txt")
@click.option("--template_name", default="template.yml")
@click.option("--only_groups")
@click.option("--with_groups")
@click.option("--without_groups")
# todo add help
def main_cli(
    without_hashes,
    with_credentials,
    without_urls,
    requirements_format,
    template_name,
    only_groups,
    with_groups,
    without_groups,
):
    groups = dict()
    groups["only"] = only_groups
    groups["with"] = with_groups
    groups["without"] = without_groups
    config = Config(
        root_dir=find_root_dir(),
        groups=groups,
        sam_exec="sam",
        requirements_format=requirements_format,
        template_name=template_name,
        without_hashes=without_hashes,
        with_credentials=with_credentials,
        without_urls=without_urls,
    )

    _ = AwsBuilder(config).build_standard()


if __name__ == "__main__":
    main_cli()
