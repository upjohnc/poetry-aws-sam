from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from cleo.io.outputs.output import Verbosity
from packaging.utils import NormalizedName, canonicalize_name
from poetry.console.exceptions import GroupNotFound
from poetry.core.packages.dependency_group import MAIN_GROUP
from poetry_plugin_export.exporter import Exporter

FORMAT_REQUIREMENTS_TXT = "requirements.txt"


class ExportLock:
    """
    Taken from ExportCommand of poetry-plugin-export.
    https://github.com/python-poetry/poetry-plugin-export/blob/2d370be73a9830a30218ebaa6e0366d974208706/src/poetry_plugin_export/command.py#L19
    """

    def __init__(self, options, poetry, io):
        self.config = options
        self._io = io
        self.poetry = poetry

    def _validate_group_options(self, group_options: dict[str, set[str]]) -> None:
        """
        Raises an error if it detects that a group is not part of pyproject.toml
        """
        invalid_options = defaultdict(set)
        for opt, groups in group_options.items():
            for group in groups:
                if not self.poetry.package.has_dependency_group(group):
                    invalid_options[group].add(opt)
        if invalid_options:
            message_parts = []
            for group in sorted(invalid_options):
                opts = ", ".join(f"<fg=yellow;options=bold>--{opt}</>" for opt in sorted(invalid_options[group]))
                message_parts.append(f"{group} (via {opts})")
            raise GroupNotFound(f"Group(s) not found: {', '.join(message_parts)}")

    def line_error(
        self,
        text: str,
        style: str | None = None,
        verbosity: Verbosity = Verbosity.NORMAL,
    ) -> None:
        """
        Write a string as information output to stderr.
        """
        styled = f"<{style}>{text}</>" if style else text

        self._io.write_error_line(styled, verbosity)

    @property
    def activated_groups(self) -> set[str]:
        groups = {}

        for key in {"with", "without", "only"}:
            groups[key] = {group.strip() for groups in self.config(key, "") for group in groups.split(",")}
        self._validate_group_options(groups)

        for opt, new, group in [
            ("no-dev", "only", MAIN_GROUP),
            ("dev", "with", "dev"),
        ]:
            if self._io.input.has_option(opt) and self.config(opt):
                self.line_error(
                    f"<warning>The `<fg=yellow;options=bold>--{opt}</>` option is"
                    f" deprecated, use the `<fg=yellow;options=bold>--{new} {group}</>`"
                    " notation instead.</warning>"
                )
                groups[new].add(group)

        if groups["only"] and (groups["with"] or groups["without"]):
            self.line_error(
                "<warning>The `<fg=yellow;options=bold>--with</>` and "
                "`<fg=yellow;options=bold>--without</>` options are ignored when used"
                " along with the `<fg=yellow;options=bold>--only</>` option."
                "</warning>"
            )

        return groups["only"] or self.default_groups.union(groups["with"]).difference(groups["without"])

    @property
    def non_optional_groups(self) -> set[str]:
        # method only required for poetry <= 1.2.0-beta.2.dev0
        return {MAIN_GROUP}

    @property
    def default_groups(self) -> set[str]:
        return {MAIN_GROUP}

    def handle(self, requirements_file: Path) -> int:
        fmt = FORMAT_REQUIREMENTS_TXT

        if not Exporter.is_format_supported(fmt):
            raise ValueError(f"Invalid export format: {fmt}")

        locker = self.poetry.locker
        if not locker.is_locked():
            self.line_error("<comment>The lock file does not exist. Locking.</comment>")
            options = []
            if self._io.is_debug():
                options.append(("-vvv", None))
            elif self._io.is_very_verbose():
                options.append(("-vv", None))
            elif self._io.is_verbose():
                options.append(("-v", None))

            self.call("lock", " ".join(options))  # type: ignore[arg-type]

        if not locker.is_fresh():
            self.line_error(
                "<warning>"
                "Warning: poetry.lock is not consistent with pyproject.toml. "
                "You may be getting improper dependencies. "
                "Run `poetry lock [--no-update]` to fix it."
                "</warning>"
            )

        # Checking extras
        if self.config("extras") and self.config("all-extras"):
            self.line_error(
                "<error>You cannot specify explicit"
                " `<fg=yellow;options=bold>--extras</>` while exporting"
                " using `<fg=yellow;options=bold>--all-extras</>`.</error>"
            )
            return 1

        extras: Iterable[NormalizedName]
        if self.config("all-extras"):
            extras = self.poetry.package.extras.keys()
        else:
            extras = {canonicalize_name(extra) for extra_opt in self.config("extras") for extra in extra_opt.split()}
            invalid_extras = extras - self.poetry.package.extras.keys()
            if invalid_extras:
                raise ValueError(f"Extra [{', '.join(sorted(invalid_extras))}] is not specified.")

        exporter = Exporter(self.poetry, self._io)
        exporter.only_groups(list(self.activated_groups))
        exporter.with_extras(list(extras))
        exporter.with_hashes(not self.config("without-hashes"))
        exporter.with_credentials(self.config("with-credentials"))
        exporter.with_urls(not self.config("without-urls"))
        exporter.export(fmt, Path.cwd(), str(requirements_file))

        return 0
