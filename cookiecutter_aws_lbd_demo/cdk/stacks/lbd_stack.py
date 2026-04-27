# -*- coding: utf-8 -*-

"""
Lambda stack function deployment mixin with versioning and event source configuration.
"""

import typing as T
import dataclasses
from functools import cached_property

from s3pathlib import S3Path

import aws_cdk as cdk
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_notifications as s3_notifications
from aws_cdk import aws_lambda as lambda_

from constructs import Construct

from ...constants import LIVE
from ...paths import PACKAGE_NAME, path_enum
from ...config.api import LbdFunc
from ...one.api import One

if T.TYPE_CHECKING:  # pragma: no cover
    from .lbd_stack_00_main import LambdaStack


@dataclasses.dataclass
class Lbd:
    """
    Dataclass to hold Lambda function and its alias.
    """
    func: lambda_.Function
    alias: lambda_.Alias


class InfraStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        one: One,
        **kwargs,
    ) -> None:
        self.one = one

        super().__init__(
            scope=scope,
            id=f"{self.one.config.project_name_slug}-lbd",
            **kwargs,
        )

    def get_lambda_layers_construct_for_function(
        self,
        lbd_func_config: LbdFunc,
    ) -> list[lambda_.LayerVersion]:
        """
        Create lambda layer declarations from config for a specific lambda function.
        """
        layers = list()
        for ith, layer_arn in enumerate(lbd_func_config.layers, start=1):
            # layer_arn can be either a full arn or a layer version id (1, 2, ...)
            if not layer_arn.startswith("arn:"):  # pragma: no cover
                final_layer_arn = (
                    f"arn:aws:lambda:{self.one.aws_region}:{self.one.aws_account_id}:layer"
                    f":{self.one.lambda_layer_name}:{layer_arn}"
                )
            else:  # pragma: no cover
                final_layer_arn = layer_arn

            layer = lambda_.LayerVersion.from_layer_version_arn(
                self,
                f"LambdaLayer{lbd_func_config.short_name_camel}{ith}",
                layer_version_arn=final_layer_arn,
            )
            layers.append(layer)
        return layers

    @cached_property
    def lambda_function_env_vars(self: "LambdaStack") -> dict[str, str]:
        env_vars = self.conf_env.env_vars
        env_vars.update(
            {
                USER_ENV_NAME: self.conf_env.env_name,
                "CONFIG_VERSION": one.config.version,
            }
        )
        return env_vars

    def get_iam_role_construct_for_function(
        self: "LambdaStack",
        lbd_func_config: LbdFunc,
    ) -> iam.IRole:
        if lbd_func_config.iam_role is None:
            return self.iam_role_for_lambda
        # use role managed by external projects
        else:  # pragma: no cover
            return iam.Role.from_role_arn(
                self,
                id=f"ImportedLambdaRole{lbd_func_config.short_name_camel}",
                role_arn=lbd_func_config.iam_role,
            )

    @cached_property
    def s3_bucket_artifacts(self: "LambdaStack") -> s3.IBucket:
        return s3.Bucket.from_bucket_name(
            self,
            id="ImportedArtifactsBucket",
            bucket_name=self.conf_env.s3dir_artifacts.bucket,
        )

    def get_lambda_function_construct_for_function(
        self: "LambdaStack",
        lbd_func_config: LbdFunc,
    ) -> lambda_.Function:
        py_ver = f"PYTHON_{one.pywf.py_ver_major}_{one.pywf.py_ver_minor}"
        runtime = getattr(lambda_.Runtime, py_ver)
        s3uri = path_enum.path_lambda_source_s3uri.read_text(encoding="utf-8").strip()
        s3path = S3Path(s3uri)
        lbd_func = lambda_.Function(
            self,
            id=f"LambdaFunc{lbd_func_config.short_name_camel}",
            current_version_options=lambda_.VersionOptions(
                removal_policy=cdk.RemovalPolicy.RETAIN,
                retry_attempts=1,
            ),
            function_name=lbd_func_config.name,
            code=lambda_.Code.from_bucket(
                bucket=self.s3_bucket_artifacts,
                key=s3path.key,
            ),
            handler=f"{PACKAGE_NAME}.lambda_function.{lbd_func_config.handler}",
            runtime=runtime,
            memory_size=lbd_func_config.memory,
            timeout=cdk.Duration.seconds(lbd_func_config.timeout),
            layers=self.get_lambda_layers_construct_for_function(lbd_func_config),
            environment=self.lambda_function_env_vars,
            role=self.get_iam_role_construct_for_function(lbd_func_config),
            reserved_concurrent_executions=lbd_func_config.reserved_concurrency,
        )
        # Add custom tags to the Lambda function
        # cdk.Tags.of(lbd_func).add("your_key_here", "your_value_here")
        return lbd_func

    def get_lambda_alias_construct_for_function(
        self: "LambdaStack",
        lbd_func_config: LbdFunc,
        lbd_func: lambda_.Function,
    ) -> lambda_.Alias:
        if lbd_func_config.live_version1 is None:
            version = lbd_func.current_version
        else:  # pragma: no cover
            version = lambda_.Version.from_version_arn(
                self,
                f"LambdaVersion1ForLive{lbd_func_config.short_name_camel}",
                version_arn=f"{lbd_func.function_arn}:{lbd_func_config.target_live_version1}",
            )

        # handle optional canary deployment
        if lbd_func_config.live_version2 is None:  # pragma: no cover
            additional_versions = None
        else:  # pragma: no cover
            if not (0.01 <= lbd_func_config.live_version2_percentage <= 0.99):
                raise ValueError("version2 percentage has to be between 0.01 and 0.99.")
            if lbd_func_config.target_live_version1 == "$LATEST":
                raise ValueError(
                    "$LATEST is not supported for an alias pointing to more than 1 version."
                )
            additional_versions = [
                lambda_.VersionWeight(
                    version=lambda_.Version.from_version_arn(
                        self,
                        f"LambdaVersion2ForLive{lbd_func_config.short_name_camel}",
                        version_arn=f"{lbd_func.function_arn}:{lbd_func_config.live_version2}",
                    ),
                    weight=lbd_func_config.live_version2_percentage,
                )
            ]

        lbd_func_alias = lambda_.Alias(
            self,
            f"LambdaAlias{lbd_func_config.short_name_camel}",
            alias_name=LIVE,
            version=version,
            additional_versions=additional_versions,
        )
        lbd_func_alias.node.add_dependency(lbd_func)
        return lbd_func_alias

    def s02_01_create_lambda_functions(self: "LambdaStack"):
        self.lambda_func_mapper: dict[str:Lbd] = dict()
        for lbd_func_config in self.conf_env.lbd_func_mappings.values():
            lbd_func = self.get_lambda_function_construct_for_function(lbd_func_config)
            lbd_func_alias = self.get_lambda_alias_construct_for_function(
                lbd_func_config, lbd_func
            )
            # put lambda function and alias into mapper, so we can access them later
            self.lambda_func_mapper[lbd_func_config.name] = Lbd(
                func=lbd_func,
                alias=lbd_func_alias,
            )

    def s02_02_configure_s3_event_source(self: "LambdaStack"):
        # ----------------------------------------------------------------------
        # Configure S3 Notification
        #
        # note:
        # based on this issue: https://github.com/aws/aws-cdk/issues/23940
        # it is impossible to use S3Bucket that is not defined in this stack
        # for ``aws_cdk.aws_lambda_event_sources.S3EventSource``
        # this is the only choice for now
        # ----------------------------------------------------------------------
        bucket = s3.Bucket.from_bucket_attributes(
            self,
            "ImportedBucket",
            bucket_arn=f"arn:aws:s3:::{self.conf_env.s3dir_source.bucket}",
        )

        # --- use latest version
        # bucket.add_event_notification(
        #     s3.EventType.OBJECT_CREATED,
        #     s3_notifications.LambdaDestination(
        #         self.lambda_func_mapper[self.env.lbd_s3sync.name][KEY_FUNC],
        #     ),
        #     s3.NotificationKeyFilter(
        #         prefix=f"{self.env.s3dir_source.key}",
        #     ),
        # )
        #
        # --- use lambda alias
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.LambdaDestination(
                lambda_.Function.from_function_attributes(
                    self,
                    f"LambdaAliasAttribute{self.conf_env.lbd_s3sync.short_name_camel}",
                    function_arn=self.lambda_func_mapper[
                        self.conf_env.lbd_s3sync.name
                    ].func.function_arn,
                    same_environment=True,
                ),
            ),
            s3.NotificationKeyFilter(
                prefix=f"{self.conf_env.s3dir_source.key}",
            ),
        )
