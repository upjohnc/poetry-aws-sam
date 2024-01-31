from dataclasses import dataclass
from os import sep
from pathlib import Path
from subprocess import run
from typing import Dict, List, Optional

import yaml
from cleo.io.io import IO
from poetry.console.application import Application
from poetry.poetry import Poetry

ROOT_FILE = "pyproject.toml"


def find_root_dir(poetry: Poetry) -> Path:
    return poetry.pyproject.path.parent


@dataclass
class AwsLambda:
    name: str
    path: Path


@dataclass
class Config:
    root_dir: Path
    groups: dict
    sam_exec: str = "sam"
    requirements_format: str = "requirements.txt"
    template_name: str = "template.yml"
    sam_build_dir_name: str = ".aws-sam/build"
    without_hashes: bool = True
    with_credentials: bool = False
    without_urls: bool = True

    @property
    def template_location(self) -> Path:
        return self.root_dir / self.template_name

    @property
    def sam_build_location(self) -> Path:
        return self.root_dir / self.sam_build_dir_name


class Sam:
    def __init__(self, sam_exec: str, template: Path):
        self.exec = sam_exec
        self.template_path = template
        self.template = self._parse_sam_template()
        self.lambdas = self._get_aws_lambdas()

    def _get_aws_lambdas(self) -> List[AwsLambda]:
        resources = self.template["Resources"]
        lambdas = {
            resource: {
                **self.template.get("Globals", {}).get("Function", {}),
                **resources[resource]["Properties"],
            }
            for resource, param in resources.items()
            if param["Type"] == "AWS::Serverless::Function"
        }
        return [
            AwsLambda(
                name=resource,
                path=Path(param["Handler"].replace(".", sep)).parent.parent,
            )
            for resource, param in lambdas.items()
            if param.get("Runtime", "").lower().startswith("python")
        ]

    def _parse_sam_template(self) -> Dict:
        yaml.SafeLoader.add_multi_constructor("!", lambda *args: None)
        return yaml.safe_load(self.template_path.read_text(encoding="utf-8"))

    def invoke_sam_build(self, build_dir: str, params: Optional[List[str]] = None):
        def_params = ["--template", str(self.template_path), "--build-dir", build_dir]
        if not params:
            params = []
        params.extend(def_params)

        return run(
            [self.exec, "build"] + params,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
