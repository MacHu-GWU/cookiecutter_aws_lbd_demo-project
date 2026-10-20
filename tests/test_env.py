# -*- coding: utf-8 -*-

import pytest

from cookiecutter_aws_lbd_demo.env import Env


def test_get_current_env_name(monkeypatch):
    env = Env()
    assert env.current_env_name == "dev"
    monkeypatch.setenv("ENV_NAME", "")
    assert env.get_current_env_name().value == "dev"
    monkeypatch.setenv("ENV_NAME", "prd")
    assert env.get_current_env_name().value == "prd"
    monkeypatch.setenv("ENV_NAME", "invalid")
    with pytest.raises(ValueError):
        env.get_current_env_name()


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.env",
        preview=False,
    )
