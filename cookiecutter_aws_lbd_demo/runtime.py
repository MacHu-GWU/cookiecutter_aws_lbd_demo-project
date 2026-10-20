# -*- coding: utf-8 -*-

"""
Runtime detection: where this code is running (a developer's machine, CI, or
inside an AWS Lambda function).

Some behavior differs by runtime. For example, locally the config comes from
``config/*.json5`` and the AWS credentials from a named profile, while inside
Lambda the config comes from SSM Parameter Store and the credentials from the
execution role. Instead of checking ``os.environ`` in every module, code asks
the module-level :data:`runtime` singleton, so the detection rule lives in one
place::

    from .runtime import runtime

    if runtime.current_runtime_name() == "aws_lambda":
        ...

Importing this module has no side effect; the runtime is worked out when asked.
"""

from __future__ import annotations

import os
import enum


class RuntimeNameEnum(enum.Enum):
    """
    Every runtime this project's code can run in.
    """

    #: A developer's machine.
    local = "local"
    #: A CI/CD runner, such as GitHub Actions.
    ci = "ci"
    #: Inside an AWS Lambda function.
    aws_lambda = "aws_lambda"


class Runtime:
    """
    Detects the current runtime.

    Use the module-level :data:`runtime` singleton instead of creating new instances.
    """

    def get_current_runtime_name(self) -> RuntimeNameEnum:
        """
        Work out the current runtime.

        ``AWS_LAMBDA_FUNCTION_NAME`` is set by the Lambda service in every
        function. The ``CI`` environment variable counts as the CI signal,
        because GitHub Actions and most other CI services set it on every runner.
        """
        if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
            return RuntimeNameEnum.aws_lambda
        elif "CI" in os.environ:
            return RuntimeNameEnum.ci
        else:
            return RuntimeNameEnum.local

    def current_runtime_name(self) -> str:
        """
        The current runtime name, such as ``"local"``.
        """
        return self.get_current_runtime_name().value


runtime = Runtime()
"""
The single :class:`Runtime` instance of this project.
"""
