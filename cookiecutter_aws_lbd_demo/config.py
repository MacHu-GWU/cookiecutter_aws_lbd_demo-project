# -*- coding: utf-8 -*-

from pydantic import BaseModel
from pydantic import Field


class Config(BaseModel):
    project_name: str = Field()
    aws_region: str = Field()
    local_aws_profile: str | None = Field(default=None)

    @property
    def project_name_snake(self) -> str:
        return self.project_name.replace("-", "_")

    @property
    def project_name_slug(self) -> str:
        return self.project_name_snake.replace("_", "-")

    @property
    def cdk_stack_name(self) -> str:
        return self.project_name_slug
