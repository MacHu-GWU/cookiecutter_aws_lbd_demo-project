# -*- coding: utf-8 -*-

"""
Deployment environment detection: which environment (dev, tst, prd) this project targets.

A single code base usually deploys the same stacks to several environments.
Instead of reading ``os.environ`` in every module, code asks the module-level
:data:`env` singleton, so the detection rule lives in one place::

    from .env import env

    if env.current_env_name == "prd":
        ...

The value is computed on first access and cached, so importing this module
has no side effect.
"""

from __future__ import annotations

import os
import enum
from functools import cached_property


class EnvNameEnum(enum.Enum):
    """
    Every environment of this project: one ``devops`` environment, plus the
    workload environments (:meth:`get_workloads`) the application is deployed to.
    Several of them may share one AWS account; resource names keep them apart.
    """

    #: Shared tooling, such as the Lambda layer every workload environment uses.
    #: Nothing of the application is deployed to it, so it has no config file,
    #: no stack, and no config in SSM.
    devops = "devops"
    #: Development, where engineers deploy and test freely.
    dev = "dev"
    #: Test, a production-like environment for integration and acceptance tests.
    tst = "tst"
    #: Production, serving real users.
    prd = "prd"

    @classmethod
    def get_workloads(cls) -> list[EnvNameEnum]:
        """
        Every workload environment, in deployment order: all but :attr:`devops`.
        """
        return [member for member in cls if member is not cls.devops]


ENV_NAME_VAR = "ENV_NAME"
"""
The environment variable that selects the current environment, such as ``ENV_NAME=prd``.
"""


class Env:
    """
    Detects the current deployment environment.

    Use the module-level :data:`env` singleton instead of creating new instances.
    """

    def get_current_env_name(self) -> EnvNameEnum:
        """
        Work out the current environment; :attr:`current_env_name` caches the result.

        It reads the ``ENV_NAME`` environment variable, and defaults to
        :attr:`EnvNameEnum.dev` when it is not set. Locally, ``.env`` may set it;
        each ``cdk-<action>-<env>-*`` mise task sets it for its own process, and the
        cdk CLI passes it on to the cdk app.

        :raises ValueError: ``ENV_NAME`` is not a member of :class:`EnvNameEnum`.
        """
        value = os.environ.get(ENV_NAME_VAR, "")
        if value:
            return EnvNameEnum(value)
        else:
            return EnvNameEnum.dev

    @cached_property
    def current_env_name(self) -> str:
        """
        The current environment name, such as ``"dev"``, computed once on first access.
        """
        return self.get_current_env_name().value


env = Env()
"""
The single :class:`Env` instance of this project.
"""
