from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
from poetry.core.pyproject.toml import PyProjectTOML
from poetry.core.packages.dependency_group import DependencyGroup
from poetry.core.packages.directory_dependency import DirectoryDependency

# Make sure to import your actual classes here
from poetry_stickywheel_plugin import StickyWheelsConfig, StickyWheelsPlugin

# Mock the external dependencies
mock_dependency = MagicMock()
mock_dependency.name = "package_name"
mock_dependency_group = MagicMock(spec=DependencyGroup)
mock_dependency_group.dependencies = [mock_dependency]


class TestStickyWheelsConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Define the base path for the test configuration files
        cls.config_base_path = Path(__file__).parent / "config_files"

    def load_config(self, filename):
        # Load the TOML configuration from the file
        config_path = self.config_base_path / filename
        return StickyWheelsConfig(PyProjectTOML(config_path))

    def test_default_strategy(self):
        config = self.load_config("default.toml")
        self.assertEqual(config.strategy, "semver")

    def test_prepare_constraint_semver(self):
        config = self.load_config("semver.toml")
        self.assertEqual(config.prepare_constraint("1.0.0"), "^1.0.0")

    def test_prepare_constraint_minimum(self):
        config = self.load_config("minimum.toml")
        self.assertEqual(config.prepare_constraint("1.0.0"), ">=1.0.0")

    def test_prepare_constraint_exact(self):
        config = self.load_config("exact.toml")
        self.assertEqual(config.prepare_constraint("1.0.0"), "1.0.0")

    def test_invalid_strategy(self):
        config = self.load_config("invalid.toml")
        with self.assertRaises(Exception):
            config.prepare_constraint("1.0.0")


class TestStickyWheelsPlugin(unittest.TestCase):
    def setUp(self):
        self.mock_application = MagicMock()
        self.mock_application.poetry = MagicMock()
        self.mock_application.poetry.pyproject = MagicMock()
        self.mock_application.poetry.package = MagicMock()
        self.mock_config = StickyWheelsConfig(self.mock_application.poetry.pyproject)
        self.plugin = StickyWheelsPlugin()

    def test_activate(self):
        # Set up the mock for the event dispatcher
        mock_event_dispatcher = MagicMock()
        self.mock_application.event_dispatcher = mock_event_dispatcher

        # Call the activate method
        self.plugin.activate(self.mock_application)

        # Assertions to verify the correct behavior
        mock_event_dispatcher.add_listener.assert_called()

    def test_update_dependency_group(self):
        # Set up IO mock
        mock_io = MagicMock()

        # Mock the dependency group and its dependencies
        mock_dependency_group = MagicMock(spec=DependencyGroup)
        mock_dependency_group.dependencies = [MagicMock(spec=DirectoryDependency)]

        # Mock the pin_dependency method to return a Dependency instance
        with patch.object(
            self.plugin, "pin_dependency", return_value=mock_dependency
        ) as mock_pin_dependency:
            # Call the update_dependency_group method
            self.plugin.update_dependency_group(mock_io, mock_dependency_group)

            # Assertions to verify the correct behavior
            mock_pin_dependency.assert_called()
            mock_dependency_group.remove_dependency.assert_called()
            mock_dependency_group.add_dependency.assert_called()

    def test_event_listener_non_relevant_command(self):
        # Mock the ConsoleCommandEvent and EventDispatcher
        mock_event = MagicMock()
        mock_event.command = MagicMock()  # Mock a non-relevant command
        mock_dispatcher = MagicMock()

        # Call the event_listener with a non-relevant command
        self.plugin.event_listener(mock_event, "", mock_dispatcher)

        # The method should early return and not execute the rest of its body,
        # so we assert that mock_event.io.write_line is never called.
        mock_event.io.write_line.assert_not_called()

    def test_event_listener_relevant_command(self):
        # Mock the ConsoleCommandEvent and EventDispatcher
        mock_event = MagicMock()
        mock_event.command = self.plugin.COMMANDS[0]()  # Mock a relevant command
        mock_event.io = MagicMock()
        mock_dispatcher = MagicMock()
        self.plugin.package = MagicMock()
        self.plugin.package.dependency_group = MagicMock(
            return_value=mock_dependency_group
        )
        self.plugin.config = self.mock_config

        # Call the event_listener with a relevant command
        with patch.object(
            self.plugin, "update_dependency_group"
        ) as mock_update_dependency_group:
            self.plugin.event_listener(mock_event, "", mock_dispatcher)

            # Assertions to verify the correct behavior
            mock_update_dependency_group.assert_called()


if __name__ == "__main__":
    unittest.main()
