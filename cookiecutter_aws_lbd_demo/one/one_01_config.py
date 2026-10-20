# -*- coding: utf-8 -*-

"""
The :attr:`~cookiecutter_aws_lbd_demo.one.one_01_config.OneConfigMixin.config` part of ``one``.
"""

from __future__ import annotations

import typing as T

from ..runtime import RuntimeNameEnum
from ..config.api import Config

if T.TYPE_CHECKING:  # pragma: no cover
    from .one_00_main import One


class OneConfigMixin:
    """
    Builds the project :class:`~cookiecutter_aws_lbd_demo.config.config_00_main.Config`.
    """

    _config: Config | None = None

    @property
    def config(self: One) -> Config:
        """
        The configuration of the current environment and runtime.

        - **local:** loaded once on first access.
        - **aws_lambda:** read again on every access, so a new value deployed with
          ``mise run config-deploy-<env>`` is picked up without redeploying the
          function. The SSM read is cached by Powertools, so within
          :data:`~cookiecutter_aws_lbd_demo.config.config_00_main.CONFIG_MAX_AGE`
          seconds this makes no AWS call.

        See :meth:`~cookiecutter_aws_lbd_demo.config.config_00_main.Config.load`.
        Assigning a config, such as ``one.config = config`` in a test, overrides both.
        """
        if self._config is not None:
            return self._config
        runtime_name = self.runtime.current_runtime_name()
        config = Config.load(
            env_name=self.env.current_env_name,
            runtime_name=runtime_name,
        )
        if runtime_name != RuntimeNameEnum.aws_lambda.value:
            self._config = config
        return config

    @config.setter
    def config(self: One, value: Config) -> None:
        self._config = value
