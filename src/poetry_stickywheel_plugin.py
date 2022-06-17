import typing

import cleo.events.console_command_event
import cleo.events.console_events
import cleo.events.event_dispatcher
import cleo.io.io
import poetry.console.application
import poetry.console.commands.build
import poetry.console.commands.publish
import poetry.core.packages.dependency
import poetry.core.packages.dependency_group
import poetry.core.packages.directory_dependency
import poetry.core.pyproject.toml
import poetry.plugins.application_plugin


class StickyWheelsPlugin(poetry.plugins.application_plugin.ApplicationPlugin):
    COMMANDS = (
        poetry.console.commands.build.BuildCommand,
        poetry.console.commands.publish.PublishCommand,
    )

    def activate(self, application: poetry.console.application.Application):
        application.event_dispatcher.add_listener(
            cleo.events.console_events.COMMAND,
            self.event_listener,
        )
        self.package = application.poetry.package

    def event_listener(
        self,
        event: cleo.events.console_command_event.ConsoleCommandEvent,
        event_name: str,
        dispatcher: cleo.events.event_dispatcher.EventDispatcher,
    ) -> None:
        command = event.command
        if not isinstance(command, self.COMMANDS):
            return

        self.update_dependency_group(event.io, self.package.dependency_group("main"))

    def update_dependency_group(
        self,
        io: cleo.io.io.IO,
        dependency_group: poetry.core.packages.dependency_group.DependencyGroup,
    ) -> None:
        io.write_line(
            "Updating dependency constraints...",
            verbosity=cleo.io.outputs.output.Verbosity.DEBUG,
        )

        for dependency in dependency_group.dependencies:
            if not isinstance(
                dependency,
                poetry.core.packages.directory_dependency.DirectoryDependency,
            ):
                continue

            pinned = self.pin_dependency(dependency)

            if dependency is pinned:
                continue

            io.write_line(
                f"  • Pinning {pinned.name} ({pinned.constraint}')",
                verbosity=cleo.io.outputs.output.Verbosity.DEBUG,
            )

            dependency_group.remove_dependency(dependency.name)
            dependency_group.add_dependency(pinned)

    def pin_dependency(
        self, dependency: poetry.core.packages.directory_dependency.DirectoryDependency
    ) -> poetry.core.packages.dependency.Dependency:
        pyproject_file = dependency.path / "pyproject.toml"

        if not pyproject_file.exists():
            return dependency

        pyproject_toml = poetry.core.pyproject.toml.PyProjectTOML(pyproject_file)

        if not pyproject_toml.is_poetry_project():
            return dependency

        name = typing.cast(str, pyproject_toml.poetry_config["name"])
        version = typing.cast(str, pyproject_toml.poetry_config["version"])

        return poetry.core.packages.dependency.Dependency(
            name,
            f"^{version}",
            groups=dependency.groups,
        )
