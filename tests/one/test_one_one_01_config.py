# -*- coding: utf-8 -*-

from cookiecutter_aws_lbd_demo.config.api import Config
from cookiecutter_aws_lbd_demo.one.api import One
from cookiecutter_aws_lbd_demo.config import config_00_main


def test_config_local():
    """
    Locally the config is loaded once, from the files.
    """
    one = One()
    assert one.config.env_name == "dev"
    assert one.config is one.config


def test_config_assigned(config: Config):
    one = One()
    one.config = config
    assert one.config is config


def test_config_aws_lambda(config: Config, monkeypatch):
    """
    Inside Lambda the config is loaded on every access (the SSM read is cached
    by Powertools), so a new value deployed to SSM is picked up.
    """
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "my-func")
    calls = []

    def load_from_ssm(name: str):
        calls.append(name)
        return config

    monkeypatch.setenv(config_00_main.CONFIG_SSM_PARAM_NAME_VAR, "/my/config")
    monkeypatch.setattr(Config, "load_from_ssm", load_from_ssm)
    one = One()
    assert one.config is config
    assert one.config is config
    assert calls == ["/my/config", "/my/config"]


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.one.one_01_config",
        preview=False,
    )
