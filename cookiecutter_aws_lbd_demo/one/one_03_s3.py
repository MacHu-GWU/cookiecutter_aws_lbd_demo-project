# -*- coding: utf-8 -*-

"""
"""

import typing as T
from functools import cached_property

from s3pathlib import S3Path

from .._version import __version__

if T.TYPE_CHECKING:  # pragma: no cover
    from .one_00_main import One


class OneS3Mixin:  # pragma: no cover
    @cached_property
    def s3bucket_data(self: "One") -> str:
        return f"{self.aws_account_alias}-{self.aws_region}-data"

    @cached_property
    def s3bucket_artifacts(self: "One") -> str:
        return f"{self.aws_account_alias}-{self.aws_region}-artifacts"

    @cached_property
    def s3dir_data(self: "One") -> S3Path:
        return S3Path(
            f"s3://{self.s3bucket_data}/projects/{self.config.project_name}/"
        ).to_dir()

    @cached_property
    def s3dir_artifacts(self: "One") -> S3Path:
        return S3Path(
            f"s3://{self.s3bucket_artifacts}/projects/{self.config.project_name}/"
        ).to_dir()

    @property
    def s3dir_lambda(self: "One") -> "S3Path":
        """
        Where you store lambda related artifacts.

        example: ``${s3dir_artifacts}/lambda/``
        """
        return self.s3dir_artifacts.joinpath("lambda").to_dir()

    @property
    def s3path_lambda_source_zip(self: "One") -> "S3Path":
        """
        Where you store lambda source zip artifact.

        example: ``${s3dir_lambda}/source/${version}/source.zip``
        """
        import aws_lambda_artifact_builder.api as aws_lambda_artifact_builder

        layout = aws_lambda_artifact_builder.SourceS3Layout(
            s3dir_lambda=self.s3dir_lambda,
        )
        s3path = layout.get_s3path_source_zip(source_version=__version__)
        return s3path

    @property
    def s3dir_source(self: "One") -> S3Path:
        return self.s3dir_data.joinpath("source").to_dir()

    @property
    def s3dir_target(self: "One") -> S3Path:
        return self.s3dir_data.joinpath("target").to_dir()
