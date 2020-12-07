from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from docker.errors import DockerException

from detectem.exceptions import DockerStartError
from detectem.splash import DockerSplashManager, requests


class TestDockerSplashManager:
    def test_init(self):
        dm = DockerSplashManager()
        assert hasattr(dm, "_instances")
        assert dm.handles_errors

    def test_docker_cli(self):
        dm = DockerSplashManager()
        cli_1 = dm.docker_cli
        cli_2 = dm.docker_cli

        assert cli_1 == cli_2

    def test_docker_cli_with_exception(self):
        dm = DockerSplashManager()

        with patch("detectem.splash.docker.from_env", side_effect=DockerException()):
            with pytest.raises(DockerStartError):
                dm.docker_cli

    def test_wait_container_valid_case(self):
        dm = DockerSplashManager()

        # Set manager metadata
        container_name = "c-1"
        dm._instances[container_name] = {"url": "http://localhost"}

        # Mock requests response
        class PingResponse:
            status_code = 200

        with patch.object(requests, "get", return_value=lambda u: PingResponse()):
            assert dm._wait_container(container_name) == None

    def test_wait_container_with_exception(self):
        dm = DockerSplashManager()

        # Set manager metadata
        container_name = "c-1"
        dm._instances[container_name] = {"url": "http://localhost"}

        with pytest.raises(DockerStartError):
            dm._wait_container(container_name)

    def test_setup_with_inexistent_docker_image(self):
        dm = DockerSplashManager()

        with patch("detectem.splash.DOCKER_SPLASH_IMAGE", "inexistent_1_2_3"):
            with pytest.raises(DockerStartError):
                dm.setup(n_instances=3)

    def test_setup_valid_case(self):
        dm = DockerSplashManager()
        n_instances = 3

        with patch("detectem.splash.NUMBER_OF_SPLASH_INSTANCES", n_instances):
            dm.setup(n_instances)
            assert len(dm._instances.keys()) == n_instances

            # Test that containers are ready
            for container_name, container_data in dm._instances.items():
                assert not container_data["in_use"]
                assert not container_data["errors"]

                c = dm.docker_cli.containers.get(container_name)
                assert c.status == "running"

            dm.teardown()

    def test_teardown(self):
        dm = DockerSplashManager()
        n_instances = 3

        with patch("detectem.splash.NUMBER_OF_SPLASH_INSTANCES", n_instances):
            dm.setup(n_instances=3)
            dm.teardown()

            # Test that containers are stopped
            for container_name in dm._instances.keys():

                c = dm.docker_cli.containers.get(container_name)
                assert c.status == "exited"

    def test_handle_error_normal_case(self):
        dm = DockerSplashManager()
        container_name = "c-1"
        dm._instances[container_name] = {"url": "http://localhost", "errors": 0}

        dm.handle_error(container_name)

        assert dm._instances[container_name]["errors"] == 1

    def test_handle_error_with_restart(self):
        dm = DockerSplashManager()
        dm.setup(n_instances=3)
        container_name = list(dm._instances.keys())[0]

        dm.handle_error(container_name)
        dm.handle_error(container_name)
        assert dm._instances[container_name]["errors"] == 2

        dm.handle_error(container_name)
        assert dm._instances[container_name]["errors"] == 0

        # Check that container was restarted
        events = dm.docker_cli.events(
            decode=True, since=datetime.utcnow() - timedelta(seconds=1)
        )
        for event in events:
            if "status" in event and event["status"] == "restart":
                assert event["Actor"]["Attributes"]["name"] == container_name
                break
        events.close()

        dm.teardown()

    def test_setup_with_container_not_starting(self):
        dm = DockerSplashManager()
        n_instances = 3

        def _conditional_mock(*args, **kwargs):
            # Raise exception for only one container
            if args[0] == "splash-detectem-0":
                raise DockerStartError()

        with patch("detectem.splash.NUMBER_OF_SPLASH_INSTANCES", n_instances):
            with patch.object(dm, "_wait_container", _conditional_mock):
                dm.setup(n_instances)
                assert dm.get_number_of_available_instances() == 2
                dm.teardown()
