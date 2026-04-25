# -*- coding: utf-8 -*-

"""
Configuration management mixin with runtime-aware loading and deployment operations.

This module provides comprehensive configuration management with adaptive loading strategies
based on runtime context, supporting local JSON files for development, SSM Parameter Store
for CI/CD and production, with automated secret management and multi-environment deployment.
"""

import typing as T
import os
from functools import cached_property

from ..paths import path_enum
from ..logger import logger
from ..runtime import runtime
from ..config import Config

if T.TYPE_CHECKING:  # pragma: no cover
    from .one_00_main import One


class OneConfigMixin:
    """
    Mixin providing runtime-aware configuration loading and management operations.
    """

    @cached_property
    def config(self: "One") -> Config:
        if runtime.is_aws_lambda:
            pass
        else:
            from dotenv import load_dotenv

            load_dotenv()
            load_dotenv(".env.shared")

        return Config(
            project_name=os.environ["PROJECT_NAME"],
            aws_region=os.environ["AWS_REGION"],
            local_aws_profile=os.environ.get("LOCAL_AWS_PROFILE"),
        )

