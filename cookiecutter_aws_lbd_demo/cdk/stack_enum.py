# -*- coding: utf-8 -*-

import dataclasses
from functools import cached_property

import aws_cdk as cdk

from ..one.api import one


@dataclasses.dataclass
class StackEnum:
    app: cdk.App = dataclasses.field()

    @cached_property
    def infra_stack(self):
        from .stacks.infra_stack import InfraStack

        return InfraStack(
            scope=self.app,
            one=one,
        )


# Create the global stack enumeration instance
app = cdk.App()

stack_enum = StackEnum(app=app)
"""
Entry point for accessing all stack instances.
"""
