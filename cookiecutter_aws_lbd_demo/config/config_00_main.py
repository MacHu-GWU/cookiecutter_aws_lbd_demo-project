# -*- coding: utf-8 -*-

from pydantic import BaseModel
from pydantic import Field

from .config_01_lbd_func import LbdFunc
from .config_02_lbd_deploy import LbdFuncDeployMixin


class Config(
    BaseModel,
    LbdFuncDeployMixin,
):
    project_name: str = Field()
    aws_region: str = Field()
    local_aws_profile: str | None = Field(default=None)

    lbd_func_py_ver: str | None = Field(default=None)
    lbd_func_hello: LbdFunc | None = Field()
    lbd_func_s3sync: LbdFunc | None = Field()

    @property
    def project_name_snake(self) -> str:
        return self.project_name.replace("-", "_")

    @property
    def project_name_slug(self) -> str:
        return self.project_name_snake.replace("_", "-")

    @property
    def cloudformation_stack_name(self) -> str:
        return self.project_name_slug

    @property
    def cloudformation_stack_url(self) -> str:
        return (
            f"https://{self.aws_region}.console.aws.amazon.com"
            f"/cloudformation/home?region={self.aws_region}#"
            f"/stacks?filteringText={self.cloudformation_stack_name}&filteringStatus=active&viewNested=true"
        )
