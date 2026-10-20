# -*- coding: utf-8 -*-

import pytest

import moto
import boto3
from aws_lambda_powertools.utilities import parameters

from cookiecutter_aws_lbd_demo.config.api import CONFIG_SSM_PARAM_NAME_VAR
from cookiecutter_aws_lbd_demo.config.api import Config


def test_load_from_local_config_file():
    config = Config.load_from_local_config_file(env_name="prd")
    assert config.env_name == "prd"
    assert config.project_name == "cookiecutter_aws_lbd_demo"
    # from the fake -secret files of conftest.py
    assert config.aws_account_id == "111122223333"
    assert config.devops_aws_account_id == "999988887777"
    assert set(config.lambda_functions) == {"hello", "s3sync"}


def test_load_unsupported_runtime():
    with pytest.raises(NotImplementedError):
        Config.load(env_name="dev", runtime_name="ci")


def test_config_fits_in_standard_ssm_parameter():
    """
    A standard SSM parameter holds 4 KB. A bigger config still deploys (as an
    advanced parameter, which costs money), so this is a warning sign, not a limit.
    """
    for env_name in ["dev", "tst", "prd"]:
        config = Config.load_from_local_config_file(env_name=env_name)
        assert len(config.model_dump_json()) < 3000


def test_load_from_ssm(config: Config, monkeypatch):
    """
    Inside Lambda the config is read from SSM, and is the same as the local one.
    While the JSON is unchanged, the same object comes back.
    """
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    parameters.clear_caches()
    with moto.mock_aws():
        ssm_client = boto3.client("ssm", region_name="us-east-1")
        ssm_client.put_parameter(
            Name=config.ssm_param_name_config,
            Value=config.model_dump_json(),
            Type="SecureString",
        )
        monkeypatch.setenv(CONFIG_SSM_PARAM_NAME_VAR, config.ssm_param_name_config)
        config_1 = Config.load(env_name="dev", runtime_name="aws_lambda")
        assert config_1 == config
        assert Config.load_from_ssm(name=config.ssm_param_name_config) is config_1

        # a new value is picked up only once the cache expires
        ssm_client.put_parameter(
            Name=config.ssm_param_name_config,
            Value=config.model_copy(
                update={"lambda_layer_version": 8}
            ).model_dump_json(),
            Type="SecureString",
            Overwrite=True,
        )
        assert Config.load_from_ssm(name=config.ssm_param_name_config) is config_1
        parameters.clear_caches()  # what happens when max_age expires
        config_2 = Config.load_from_ssm(name=config.ssm_param_name_config)
        assert config_2.lambda_layer_version == 8
    parameters.clear_caches()


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.config.config_00_main",
        preview=False,
    )
