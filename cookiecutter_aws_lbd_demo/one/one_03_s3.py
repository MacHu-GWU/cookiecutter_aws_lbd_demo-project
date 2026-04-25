# -*- coding: utf-8 -*-

"""
"""

import typing as T
from functools import cached_property

import boto3
from s3pathlib import S3Path

from ..runtime import runtime

if T.TYPE_CHECKING:  # pragma: no cover
    from .one_00_main import One


class OneS3Mixin:  # pragma: no cover
    @cached_property
    def s3bucket(self: "One") -> str:
        return f"s3://{self.aws_account_alias}-{self.aws_region}-data"

    @cached_property
    def s3dir_data(self: "One") -> S3Path:
        return S3Path(
            f"s3://{self.s3bucket}/projects/{self.config.project_name}/"
        ).to_dir()

    @property
    def s3dir_source(self: "One") -> S3Path:
        return self.s3dir_data.joinpath("source").to_dir()

    @property
    def s3dir_target(self: "One") -> S3Path:
        return self.s3dir_data.joinpath("target").to_dir()
