# -*- coding: utf-8 -*-

import aws_cdk as cdk
from aws_cdk import aws_iam as iam

from constructs import Construct

from ...one.api import One


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
            id=f"{self.one.config.project_name_slug}-infra",
            **kwargs,
        )

        self.s01_create_iam_roles()

    def s01_create_iam_roles(self):
        """
        IAM related resources.

        Ref:

        - IAM Object quotas: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html#reference_iam-quotas-entities
        """

        self.stat_s3_bucket_read = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:ListBucket",
                "s3:GetObject",
                "s3:GetObjectAttributes",
                "s3:GetObjectTagging",
            ],
            resources=[
                f"arn:aws:s3:::{self.one.s3dir_data.bucket}",
                f"arn:aws:s3:::{self.one.s3dir_data.bucket}/{self.one.s3dir_data.key}*",
            ],
        )

        self.stat_s3_bucket_write = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:PutObjectTagging",
                "s3:DeleteObjectTagging",
            ],
            resources=[
                f"arn:aws:s3:::{self.one.s3dir_data.bucket}",
                f"arn:aws:s3:::{self.one.s3dir_data.bucket}/{self.one.s3dir_data.key}*",
            ],
        )

        # declare iam role
        self.iam_role_for_lambda = iam.Role(
            scope=self,
            id="IamRoleForLambda",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=f"{self.one.config.project_name_snake}-{cdk.Aws.REGION}-lambda",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
            inline_policies={
                f"{self.one.config.project_name_snake}-{cdk.Aws.REGION}-lambda": iam.PolicyDocument(
                    statements=[
                        self.stat_s3_bucket_read,
                        self.stat_s3_bucket_write,
                    ]
                )
            },
        )

        self.output_iam_role_for_lambda_arn = cdk.CfnOutput(
            self,
            "IamRoleForLambdaArn",
            value=self.iam_role_for_lambda.role_arn,
            export_name=f"{self.one.config.project_name_slug}-lambda-role-arn",
        )
