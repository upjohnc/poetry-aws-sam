from collections import defaultdict
from pathlib import Path

from poetry.console.application import Application
from poetry.console.exceptions import GroupNotFound
from poetry.poetry import Poetry
from poetry_plugin_export.exporter import Exporter

MAIN_GROUP = "main"


class ExportLock:
    """
    Taken from ExportCommand of poetry-plugin-export.
    https://github.com/python-poetry/poetry-plugin-export/blob/2d370be73a9830a30218ebaa6e0366d974208706/src/poetry_plugin_export/command.py#L19
    """

    _poetry: Poetry | None = None
    # options = [  # noqa: RUF012
    #     option(
    #         "format",
    #         "f",
    #         "Format to export to. Currently, only constraints.txt and" " requirements.txt are supported.",
    #         flag=False,
    #         default=Exporter.FORMAT_REQUIREMENTS_TXT,
    #     ),
    #     option("output", "o", "The name of the output file.", flag=False),
    #     option("without-hashes", None, "Exclude hashes from the exported file."),
    #     option(
    #         "without-urls",
    #         None,
    #         "Exclude source repository urls from the exported file.",
    #     ),
    #     option(
    #         "dev",
    #         None,
    #         "Include development dependencies. (<warning>Deprecated</warning>)",
    #     ),
    #     *GroupCommand._group_dependency_options(),
    #     option(
    #         "extras",
    #         "E",
    #         "Extra sets of dependencies to include.",
    #         flag=False,
    #         multiple=True,
    #     ),
    #     option("all-extras", None, "Include all sets of extra dependencies."),
    #     option("with-credentials", None, "Include credentials for extra indices."),
    # ]

    def __init__(self):
        self._application: Application = Application()

    @property
    def poetry(self) -> Poetry:
        if self._poetry is None:
            return self.get_application().poetry

        return self._poetry

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

    @property
    def activated_groups(self) -> set[str]:
        groups = {}
        # todo : change how groups are created
        # self.option(key, "")
        group_option = [MAIN_GROUP]

        for key in {"with", "without", "only"}:
            if key == "only":
                groups[key] = {group.strip() for groups in group_option for group in groups.split(",")}
            else:
                groups[key] = {}
        self._validate_group_options(groups)

        if groups["only"] and (groups["with"] or groups["without"]):
            print(
                "<warning>The `<fg=yellow;options=bold>--with</>` and "
                "`<fg=yellow;options=bold>--without</>` options are ignored when used"
                " along with the `<fg=yellow;options=bold>--only</>` option."
                "</warning>"
            )

        return groups["only"]  # or self.default_groups.union(groups["with"]).difference(groups["without"])

    @property
    def application(self) -> Application | None:
        return self._application

    def get_application(self) -> Application:
        from poetry.console.application import Application

        application = self.application
        assert isinstance(application, Application)
        return application

    def handle(self) -> int:
        fmt = "requirements.txt"

        output = Path(".aws-sam/build/HelloWorldFunction/poetry_aws_sam/requirements.txt")

        # locker = self.poetry.locker
        # if not locker.is_locked()
        #     self.line_error("<comment>The lock file does not exist. Locking.</comment>")
        #     options = []
        #     if self.io.is_debug():
        #         options.append(("-vvv", None))
        #     elif self.io.is_very_verbose():
        #         options.append(("-vv", None))
        #     elif self.io.is_verbose():
        #         options.append(("-v", None))

        #     self.call("lock", " ".join(options))  # type: ignore[arg-type]

        # if not locker.is_fresh():
        #     self.line_error(
        #         "<warning>"
        #         "Warning: poetry.lock is not consistent with pyproject.toml. "
        #         "You may be getting improper dependencies. "
        #         "Run `poetry lock [--no-update]` to fix it."
        #         "</warning>"
        #     )

        # Checking extras
        # if self.option("extras") and self.option("all-extras"):
        #     self.line_error(
        #         "<error>You cannot specify explicit"
        #         " `<fg=yellow;options=bold>--extras</>` while exporting"
        #         " using `<fg=yellow;options=bold>--all-extras</>`.</error>"
        #     )
        #     return 1

        # extras = self.poetry.package.extras.keys()
        # extras: Iterable[NormalizedName]
        # if self.option("all-extras"):
        #     extras = self.poetry.package.extras.keys()
        # else:
        #     extras = {canonicalize_name(extra) for extra_opt in self.option("extras") for extra in extra_opt.split()}
        #     invalid_extras = extras - self.poetry.package.extras.keys()
        #     if invalid_extras:
        #         raise ValueError(f"Extra [{', '.join(sorted(invalid_extras))}] is not specified.")

        exporter = Exporter(self.poetry, None)  # todo: figure out the IO thing
        exporter.only_groups(list(self.activated_groups))
        # exporter.with_extras(list(extras))
        # exporter.with_hashes(not self.option("without-hashes"))
        # exporter.with_credentials(self.option("with-credentials"))
        # exporter.with_urls(not self.option("without-urls"))
        exporter.export(fmt, Path.cwd(), output)

        return 0
