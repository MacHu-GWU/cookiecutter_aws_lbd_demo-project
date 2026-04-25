# -*- coding: utf-8 -*-

"""
DevOps automation mixin for Lambda deployment and layer management operations.

This module provides comprehensive DevOps automation including containerized Lambda layer building,
source artifact packaging, cross-account permission management, and layer version cleanup with
integration to AWS CodeArtifact for private dependency management.
"""

import typing as T

from ..paths import path_enum
from ..lazy_imports import simple_aws_lambda
from ..lazy_imports import aws_lambda_artifact_builder

if T.TYPE_CHECKING:  # pragma: no cover
    from .one_00_main import One


class OneDevOpsMixin:  # pragma: no cover
    """
    Mixin providing Lambda deployment automation and DevOps operations.
    """

    def build_lambda_layer_in_container(self: "One"):
        """
        Build Lambda layer in containerized environment with CodeArtifact integration and cross-account permissions.
        """
        # Build and publish Lambda Layer
        workflow = (
            aws_lambda_artifact_builder.LambdaLayerBuildPackageUploadAndPublishWorkflow(
                layer_name=self.config.lambda_layer_name,
                py_ver_major=self.config.lbd_func_py_ver_major,
                py_ver_minor=self.config.lbd_func_py_ver_minor,
                is_arm=False,
                path_pyproject_toml=path_enum.path_pyproject_toml,
                s3dir_lambda=self.s3dir_lambda,
                s3_client=self.s3_client,
                lambda_client=self.lambda_client,
                layer_build_tool=aws_lambda_artifact_builder.LayerBuildToolEnum.uv,
                ignore_package_list=None,
                publish_layer_version_kwargs=None,
            )
        )
        layer_deployment = workflow.run()

    def cleanup_old_layer_versions(self: "One"):
        """
        Clean up old Lambda layer versions keeping only the most recent version.
        """
        deleted_versions = simple_aws_lambda.cleanup_old_layer_versions(
            lambda_client=self.lambda_client,
            layer_name=self.config.lambda_layer_name,
            keep_last_n_versions=1,
            keep_versions_newer_than_seconds=0,
            real_run=True,
        )
        print(f"{deleted_versions = }")

    def build_lambda_source(self: "One"):
        """
        Build Lambda source artifacts using pip and create deployment-ready zip package.
        """
        result = aws_lambda_artifact_builder.build_package_upload_source_artifacts(
            s3_client=self.s3_client,
            dir_project_root=path_enum.dir_project_root,
            s3dir_lambda=self.s3dir_lambda,
            skip_prompt=True,
        )
        uri = result.s3path_source_zip.uri
        path_enum.path_lambda_source_s3uri.write_text(uri, encoding="utf-8")
