from collections import defaultdict
from pathlib import Path

from cleo.io.inputs.string_input import StringInput
from poetry.console.exceptions import GroupNotFound
from poetry.poetry import Poetry
from poetry_plugin_export.exporter import Exporter

from poetry_aws_sam.aws import ChadApplication, Config

MAIN_GROUP = "main"


# class ExportLock(ChadApplication):
class ExportLock:
    """
    Taken from ExportCommand of poetry-plugin-export.
    https://github.com/python-poetry/poetry-plugin-export/blob/2d370be73a9830a30218ebaa6e0366d974208706/src/poetry_plugin_export/command.py#L19
    """

    _poetry: Poetry | None = None

    def __init__(self, config: Config):
        # self._application: Application = Application()
        self.config = config
        self.chad = ChadApplication()
        # super().__init__()

    # @property
    # def poetry(self) -> Poetry:
    #     if self._poetry is None:
    #         return self.get_application().poetry

    #     return self._poetry

    def _validate_group_options(self, group_options: dict[str, set[str]]) -> None:
        """
        Raises an error if it detects that a group is not part of pyproject.toml
        """
        invalid_options = defaultdict(set)
        for opt, groups in group_options.items():
            for group in groups:
                if not self.chad.poetry.package.has_dependency_group(group):
                    invalid_options[group].add(opt)
        if invalid_options:
            message_parts = []
            for group in sorted(invalid_options):
                opts = ", ".join(f"<fg=yellow;options=bold>--{opt}</>" for opt in sorted(invalid_options[group]))
                message_parts.append(f"{group} (via {opts})")
            raise GroupNotFound(f"Group(s) not found: {', '.join(message_parts)}")

    @property
    def non_optional_groups(self) -> set[str]:
        return {group.name for group in self.chad.poetry.package._dependency_groups.values() if not group.is_optional()}

    @property
    def default_groups(self) -> set[str]:
        """
        The groups that are considered by the command by default.

        Can be overridden to adapt behavior.
        """
        return self.non_optional_groups

    @property
    def activated_groups(self) -> set[str]:
        # todo: add test for this method
        groups = {}

        for key in {"with", "without", "only"}:
            group_list = self.config.groups.get(key, None)
            if group_list is not None:
                groups[key] = {group.strip() for group in group_list.split(",")}

        self._validate_group_options(groups)

        for opt, new, group in [
            ("no-dev", "only", MAIN_GROUP),
            ("dev", "with", "dev"),
        ]:
            if self.config.groups.get(opt, None) is not None:
                self.chad.io.write_error_line(
                    f"<warning>The `<fg=yellow;options=bold>--{opt}</>` option is"
                    f" deprecated, use the `<fg=yellow;options=bold>--{new} {group}</>`"
                    " notation instead.</warning>"
                )
                groups[new].add(group)

        if "only" in groups.keys() and ("with" in groups.keys() or "without" in groups.keys()):
            self.chad.io.write_error_line(
                "<warning>The `<fg=yellow;options=bold>--with</>` and "
                "`<fg=yellow;options=bold>--without</>` options are ignored when used"
                " along with the `<fg=yellow;options=bold>--only</>` option."
                "</warning>"
            )

        return groups.get("only", None) or self.default_groups.union(groups.get("with", {})).difference(
            groups.get("without", {})
        )

    # @property
    # def application(self) -> Application | None:
    #     return self._application

    # @property
    # def io(self) -> IO:
    #     return self._application.create_io()

    # def call(self, name: str, args: str | None = None) -> int:
    #     """
    #     Call another command.
    #     """
    #     assert self.application is not None
    #     command = self.application.get(name)

    #     return self.application._run_command(command, self.io.with_input(StringInput(args or "")))

    # def get_application(self) -> Application:
    #     from poetry.console.application import Application

    #     application = self.application
    #     assert isinstance(application, Application)
    #     return application

    def handle(self, requirements_file: Path) -> int:
        locker = self.chad.poetry.locker
        if not locker.is_locked():
            self.chad.io.write_error_line("<comment>The lock file does not exist. Locking.</comment>")
            options = []
            if self.chad.io.is_debug():
                options.append(("-vvv", None))
            elif self.chad.io.is_very_verbose():
                options.append(("-vv", None))
            elif self.chad.io.is_verbose():
                options.append(("-v", None))

            self.chad.call("lock", " ".join(options))  # type: ignore[arg-type]

        if not locker.is_fresh():
            self.chad.io.write_error_line(
                "<warning>"
                "Warning: poetry.lock is not consistent with pyproject.toml. "
                "You may be getting improper dependencies. "
                "Run `poetry lock [--no-update]` to fix it."
                "</warning>"
            )

        exporter = Exporter(self.chad.poetry, self.chad.io)
        exporter.only_groups(list(self.activated_groups))
        exporter.with_hashes(not self.config.without_hashes)
        exporter.with_credentials(self.config.with_credentials)
        exporter.with_urls(not self.config.without_urls)
        exporter.export(self.config.requirements_format, Path.cwd(), str(requirements_file))

        return 0
