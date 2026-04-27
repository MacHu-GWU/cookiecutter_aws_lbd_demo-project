# -*- coding: utf-8 -*-

from soft_deps.api import MissingDependency

try:
    import simple_aws_lambda.api as simple_aws_lambda
except ImportError as e:  # pragma: no cover
    simple_aws_lambda = MissingDependency(
        name="simple_aws_lambda",
        error_message=f"please do 'make install-dev'",
    )

try:
    import aws_lbd_art_builder_uv.api as aws_lbd_art_builder_uv
except ImportError as e:  # pragma: no cover
    aws_lbd_art_builder_uv = MissingDependency(
        name="aws_lbd_art_builder_uv",
        error_message=f"please do 'uv sync --extra dev'",
    )

try:
    import aws_lbd_art_builder_core.api as aws_lbd_art_builder_core
except ImportError as e:  # pragma: no cover
    aws_lbd_art_builder_core = MissingDependency(
        name="aws_lbd_art_builder_core",
        error_message=f"please do 'uv sync --extra dev'",
    )

try:
    import rstobj
except ImportError as e:  # pragma: no cover
    rstobj = MissingDependency(
        name="rstobj",
        error_message=f"please do 'make install-dev'",
    )
