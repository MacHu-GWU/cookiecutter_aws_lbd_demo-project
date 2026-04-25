# -*- coding: utf-8 -*-

"""
Lambda function deployment related configurations.
"""

import typing as T
import dataclasses

from s3pathlib import S3Path
from ..lazy_imports import aws_lambda_artifact_builder

from .._version import __version__


if T.TYPE_CHECKING:  # pragma: no cover
    from .config_00_main import Env


@dataclasses.dataclass
class LbdFuncDeployMixin:
    """
    Lambda function deployment related configurations.
    """

    @property
    def lambda_layer_name(self: "Env") -> str:
        """
        Lambda function layer name.

        Because the Lambda layer is an immutable artifact, we only need one
        lambda layer across all envs, so we don't need to include env name in the
        layer name.
        """

        return self.project_name_snake

    @property
    def s3dir_lambda(self: "Env") -> "S3Path":
        """
        Where you store lambda related artifacts.

        example: ``${s3dir_artifacts}/lambda/``
        """
        return self.s3dir_artifacts.joinpath("lambda").to_dir()

    @property
    def s3path_lambda_source_zip(self: "Env") -> "S3Path":
        """
        Where you store lambda source zip artifact.

        example: ``${s3dir_lambda}/source/${version}/source.zip``
        """
        layout = aws_lambda_artifact_builder.SourceS3Layout(
            s3dir_lambda=self.s3dir_lambda,
        )
        s3path = layout.get_s3path_source_zip(source_version=__version__)
        return s3path
