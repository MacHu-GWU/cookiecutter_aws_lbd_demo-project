# -*- coding: utf-8 -*-

import aws_cdk as cdk
from constructs import Construct

from ...config import Config


class InfraStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        config: Config,
        **kwargs,
    ) -> None:
        self.config = config

        super().__init__(
            scope=scope,
            id=f"{config.project_name_snake}-infra",
            **kwargs,
        )

        self.create_iam_role()

    def create_iam_role(self):
        pass
