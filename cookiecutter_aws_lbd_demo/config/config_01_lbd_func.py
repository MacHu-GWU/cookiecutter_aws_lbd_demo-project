# -*- coding: utf-8 -*-

"""
Lambda function configurations.
"""

import typing as T
from pydantic import BaseModel, Field, PrivateAttr
from boltons.strutils import slugify, under2camel

from ..constants import LATEST

if T.TYPE_CHECKING:  # pragma: no cover
    from .config_00_main import Config


class LbdFunc(BaseModel):
    """
    Represent a lambda function.
    """

    short_name: str = Field()
    handler: str = Field()
    timeout: int = Field()
    memory: int = Field()
    iam_role: str | None = Field(default=None)
    env_vars: dict[str, str] = Field(default_factory=dict)
    layers: list[str] = Field(default_factory=list)
    subnet_ids: list[str] | None = Field(default_factory=list)
    security_group_ids: list[str] | None = Field(default_factory=list)
    reserved_concurrency: int | None = Field(default=None)
    live_version1: str | None = Field(default=None)
    live_version2: str | None = Field(default=None)
    live_version2_percentage: float | None = Field(default=None)

    _config: "Config" = PrivateAttr()

    @property
    def config(self) -> "Config":
        """
        The config this lambda function belongs to.
        """
        return self._config

    @property
    def name(self) -> str:
        """
        Full name of the Lambda function.
        """
        return f"{self.config.project_name_snake}-{self.short_name}"

    @property
    def short_name_slug(self) -> str:
        """
        Example: ``my-func``
        """
        return slugify(self.short_name, delim="-")

    @property
    def short_name_snake(self) -> str:
        """
        Example: ``my_func``
        """
        return slugify(self.short_name, delim="_")

    @property
    def short_name_camel(self) -> str:
        """
        The lambda function short name in camel case. This is usually used
        in CloudFormation logic ID.

        Example: ``MyFunc``
        """
        return under2camel(slugify(self.short_name, delim="_"))
