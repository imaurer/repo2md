import pytest
from repo2md import Config


@pytest.fixture(scope="function")
def config():
    config = Config()
    config.quiet = True
    assert config.quiet is True
    return config


def test_singleton_instance(config):
    assert config.quiet is True
    too = Config()
    assert too is config
    assert config is too
    assert config.quiet
    assert too.quiet is True


def test_config_update(config):
    assert config.verbose is False
    assert config.quiet is True

    too = Config()
    too.update_config(**{"verbose": True, "quiet": False, "max_size": 2048})
    assert config.verbose is True
    assert config.quiet is False
    assert config.max_size == 2048
