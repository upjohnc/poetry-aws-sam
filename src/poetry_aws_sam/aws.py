import os
from dataclasses import dataclass
from os import sep
from pathlib import Path
from subprocess import run  # nosec
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class AwsLambda:
    name: str
    path: Path


class Sam:  # pylint: disable=too-few-public-methods
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


class Application:
    """
    The way output is displayed can be [configured](../config/hatch.md#terminal) by users.

    !!! important
        Never import this directly; Hatch judiciously decides if a type of plugin requires
        the capabilities herein and will grant access via an attribute.
    """

    def __init__(self) -> None:
        self.__verbosity = int(os.environ.get("HATCH_VERBOSE", "0")) - int(os.environ.get("HATCH_QUIET", "0"))

    @property
    def verbosity(self) -> int:
        """
        The verbosity level of the application, with 0 as the default.
        """
        return self.__verbosity

    @staticmethod
    def display(message: str = "", **kwargs: Any) -> None:  # noqa: ARG004
        # Do not document
        _display(message)

    def display_info(self, message: str = "", **kwargs: Any) -> None:  # noqa: ARG002
        """
        Meant to be used for messages conveying basic information.
        """
        if self.__verbosity >= 0:
            _display(message)

    def display_waiting(self, message: str = "", **kwargs: Any) -> None:  # noqa: ARG002
        """
        Meant to be used for messages shown before potentially time consuming operations.
        """
        if self.__verbosity >= 0:
            _display(message)

    def display_success(self, message: str = "", **kwargs: Any) -> None:  # noqa: ARG002
        """
        Meant to be used for messages indicating some positive outcome.
        """
        if self.__verbosity >= 0:
            _display(message)

    def display_warning(self, message: str = "", **kwargs: Any) -> None:  # noqa: ARG002
        """
        Meant to be used for messages conveying important information.
        """
        if self.__verbosity >= -1:
            _display(message)

    def display_error(self, message: str = "", **kwargs: Any) -> None:  # noqa: ARG002
        """
        Meant to be used for messages indicating some unrecoverable error.
        """
        if self.__verbosity >= -2:  # noqa: PLR2004
            _display(message)

    def display_debug(self, message: str = "", level: int = 1, **kwargs: Any) -> None:  # noqa: ARG002
        """
        Meant to be used for messages that are not useful for most user experiences.
        The `level` option must be between 1 and 3 (inclusive).
        """
        if not 1 <= level <= 3:  # noqa: PLR2004
            error_message = "Debug output can only have verbosity levels between 1 and 3 (inclusive)"
            raise ValueError(error_message)

        if self.__verbosity >= level:
            _display(message)

    def display_mini_header(self, message: str = "", **kwargs: Any) -> None:  # noqa: ARG002
        if self.__verbosity >= 0:
            _display(f"[{message}]")

    def abort(self, message: str = "", code: int = 1, **kwargs: Any) -> None:  # noqa: ARG002
        """
        Terminate the program with the given return code.
        """
        if message and self.__verbosity >= -2:  # noqa: PLR2004
            _display(message)

        sys.exit(code)


_display = print
