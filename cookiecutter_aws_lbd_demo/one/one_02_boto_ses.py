# -*- coding: utf-8 -*-

"""
Boto session management mixin for AWS service access and credential handling.
"""

import typing as T
from functools import cached_property

import boto3

from ..runtime import runtime

if T.TYPE_CHECKING:  # pragma: no cover
    from .one_00_main import One


class OneBotoSesMixin:  # pragma: no cover
    """
    Mixin providing lazy-loaded boto session management and AWS console access.
    """

    @cached_property
    def boto_ses(self: "One") -> boto3.Session:
        if runtime.is_aws_lambda:
            return boto3.Session(region_name=self.config.aws_region)
        else:
            return boto3.Session(
                profile_name=self.config.local_aws_profile,
                region_name=self.config.aws_region,
            )
