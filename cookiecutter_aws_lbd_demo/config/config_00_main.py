# -*- coding: utf-8 -*-

"""
The top-level configuration model.

:class:`Config` holds every project-level setting the stacks, the scripts and
the Lambda functions need. Resource names are not written here but derived in
``config_01_name.py``.

To add a group of related settings, put them in a new numbered module
(``config_02_xxx.py``, ...) as a mixin or a nested model, then add it to
:class:`Config` here. The number gives the reading order: lower modules are
more foundational.

**Where the values come from:**

- **local:** ``config/*.json5`` files at the repo root, read by
  :meth:`Config.load_from_local_config_file`.
- **aws_lambda:** one SSM SecureString parameter per environment, holding the
  whole config as JSON, read by :meth:`Config.load_from_ssm`. ``mise run
  config-deploy-<env>`` writes it from the local files, see
  :meth:`~cookiecutter_aws_lbd_demo.one.one_03_devops.OneDevOpsMixin.deploy_config`.

So the Lambda function sees exactly the same :class:`Config` object as the
developer, and a config change takes effect without redeploying the function
(after the parameter cache expires, see :data:`CONFIG_MAX_AGE`).
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel
from pydantic import Field

from ..paths import path_enum
from ..runtime import RuntimeNameEnum
from .config_01_name import ConfigNameMixin


CONFIG_SSM_PARAM_NAME_VAR = "CONFIG_SSM_PARAM_NAME"
"""
The Lambda environment variable that names the SSM parameter holding the config;
the lbd stack sets it.
"""

CONFIG_MAX_AGE = 300
"""
How long (seconds) a Lambda container caches the config before it reads SSM again.
"""


class LambdaFunction(BaseModel):
    """
    Settings of one Lambda function. The function name is derived from its key
    in :attr:`Config.lambda_functions`, see
    :meth:`~cookiecutter_aws_lbd_demo.config.config_01_name.ConfigNameMixin.get_lambda_function_name`.
    """

    # fmt: off
    handler: str = Field()  #: Attribute name in ``lambda_function.py``, such as ``hello_handler``.
    timeout: int = Field()  #: Timeout in seconds.
    memory: int = Field()  #: Memory size in MB.
    reserved_concurrency: int | None = Field(default=None)  #: Reserved concurrent executions, ``None`` for unreserved.
    # fmt: on


class Config(
    BaseModel,
    ConfigNameMixin,
):
    """
    Project-wide settings of one environment, validated on load.

    Every resource name is derived from these values in
    :class:`~cookiecutter_aws_lbd_demo.config.config_01_name.ConfigNameMixin`.
    """

    # fmt: off
    project_name: str = Field()  #: Project name in snake_case or slug-case, such as ``my_project``.
    env_name: str = Field()  #: The environment these values are for, such as ``dev``.
    aws_account_id: str = Field()  #: The AWS account this environment deploys to, kept in ``config-<env>-secret.json5``.
    aws_region: str = Field()  #: The AWS region this environment deploys to.
    devops_aws_account_id: str = Field()  #: The DEVOPS account that owns the Lambda layer, kept in ``config-shared-secret.json5``.
    devops_s3_bucket_artifacts: str = Field()  #: Artifacts bucket in the DEVOPS account, where layer zips go.
    s3_bucket_data: str = Field()  #: Pre-existing data bucket of this environment; this project only uses its own prefix.
    lambda_python_version: str = Field()  #: Lambda Python version, such as ``3.12``.
    lambda_layer_version: int = Field()  #: The layer version this environment uses, printed by ``mise run lambda-layer-deploy``.
    lambda_layer_build_in_container: bool = Field(default=False)  #: Build the layer in the AWS SAM image (needs Docker) instead of on the host.
    lambda_functions: dict[str, LambdaFunction] = Field()  #: Every Lambda function, by short name, such as ``hello``.
    # fmt: on

    @classmethod
    def load_from_local_config_file(
        cls,
        env_name: str,
        dir_config: Path | None = None,
    ) -> Config:
        """
        Load the config of one environment from the json5 files in ``dir_config``.

        Four files are merged, a later one overriding the keys of an earlier one:
        ``config-shared.json5``, ``config-shared-secret.json5``,
        ``config-<env_name>.json5``, ``config-<env_name>-secret.json5``.
        The ``-secret`` files are git-ignored and may be missing; the others are required.
        ``config/example/`` shows the shape of every file.

        :param env_name: such as ``dev``, see :class:`~cookiecutter_aws_lbd_demo.env.EnvNameEnum`.
        :param dir_config: the folder of the config files; defaults to ``path_enum.dir_config``.
        """
        # json5 is a dev dependency; it is not in the Lambda layer.
        import json5

        if dir_config is None:
            dir_config = path_enum.dir_config
        data = {}
        for name in ["shared", env_name]:
            path = dir_config / f"config-{name}.json5"
            data.update(json5.loads(path.read_text(encoding="utf-8")))
            path_secret = dir_config / f"config-{name}-secret.json5"
            if path_secret.exists():
                data.update(json5.loads(path_secret.read_text(encoding="utf-8")))
        data["env_name"] = env_name
        return cls(**data)

    @classmethod
    def load_from_ssm(
        cls,
        name: str,
        max_age: int = CONFIG_MAX_AGE,
    ) -> Config:
        """
        Load the config from the SSM parameter ``name``, through the Powertools
        parameter cache: within ``max_age`` seconds no AWS call is made.
        """
        from aws_lambda_powertools.utilities import parameters

        value = parameters.get_parameter(name, decrypt=True, max_age=max_age)
        return _parse_config_json(value)

    @classmethod
    def load(
        cls,
        env_name: str,
        runtime_name: str,
    ) -> Config:
        """
        Load the config the way the current runtime supports.

        :param env_name: such as ``dev``.
        :param runtime_name: such as ``local``, see :class:`~cookiecutter_aws_lbd_demo.runtime.RuntimeNameEnum`.

        :raises NotImplementedError: on any other runtime, such as CI.
        """
        if runtime_name == RuntimeNameEnum.local.value:
            return cls.load_from_local_config_file(env_name=env_name)
        elif runtime_name == RuntimeNameEnum.aws_lambda.value:
            return cls.load_from_ssm(name=os.environ[CONFIG_SSM_PARAM_NAME_VAR])
        else:
            raise NotImplementedError(
                f"loading config on runtime {runtime_name!r} is not supported, "
                "deploy from a local machine"
            )


_last_config_json: str | None = None
_last_config: Config | None = None


def _parse_config_json(value: str) -> Config:
    """
    Parse the config JSON, reusing the last :class:`Config` object while the
    JSON is unchanged, so the cached properties of the names are not rebuilt on
    every invocation.
    """
    global _last_config_json, _last_config
    if value != _last_config_json:
        _last_config = Config.model_validate_json(value)
        _last_config_json = value
    return _last_config
