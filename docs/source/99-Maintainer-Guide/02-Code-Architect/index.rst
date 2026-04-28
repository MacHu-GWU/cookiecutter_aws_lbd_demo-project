.. _Code-Architecture:

Code Architecture
==============================================================================

This document explains how the codebase is organized, how modules depend on
each other, and how to extend the project with new resources.


Directory Structure
------------------------------------------------------------------------------

::

    cookiecutter_aws_lbd_demo-project/
    │
    ├── .env                          # Secret env vars (LOCAL_AWS_PROFILE) — git-ignored
    ├── .env.shared                   # Non-secret env vars — committed to git
    ├── mise.toml                     # Tool versions + task runner definitions
    ├── pyproject.toml                # Python package metadata and dependencies
    │
    ├── cookiecutter_aws_lbd_demo/    # ── Main Python package ──
    │   ├── __init__.py               # Package root
    │   ├── api.py                    # Public API re-exports
    │   ├── _version.py               # Version (from pyproject.toml metadata)
    │   ├── constants.py              # Project-wide constants (LATEST, LIVE, etc.)
    │   ├── paths.py                  # Centralized absolute path references
    │   ├── runtime.py                # Runtime detection (Lambda vs local)
    │   ├── logger.py                 # Shared logger instance
    │   ├── lazy_imports.py           # Dev-only dependency lazy loading
    │   ├── lambda_function.py        # Lambda handler entry point (re-exports)
    │   │
    │   ├── config/                   # Pydantic configuration models
    │   │   ├── config_00_main.py     # Top-level Config class
    │   │   ├── config_01_lbd_func.py # Per-function LbdFunc model
    │   │   ├── config_02_lbd_deploy.py # Deployment mixin (layer name, etc.)
    │   │   └── api.py                # Public re-exports
    │   │
    │   ├── one/                      # Singleton resource access (lazy-loaded)
    │   │   ├── one_00_main.py        # One class (mixin composition)
    │   │   ├── one_01_config.py      # Config loading mixin
    │   │   ├── one_02_boto_ses.py    # Boto session mixin
    │   │   ├── one_03_s3.py          # S3 path mixin
    │   │   ├── one_04_devops.py      # DevOps automation mixin
    │   │   └── api.py                # Public re-exports
    │   │
    │   ├── lbd/                      # Lambda function handlers
    │   │   ├── base.py               # BaseInput / BaseOutput (Pydantic)
    │   │   ├── hello.py              # Simple greeting function
    │   │   └── s3sync.py             # S3 event-driven copy function
    │   │
    │   ├── cdk/                      # CDK infrastructure-as-code
    │   │   ├── stack_enum.py          # Stack registry (lazy entry point)
    │   │   └── stacks/
    │   │       ├── infra_stack.py         # IAM roles, policies
    │   │       ├── infra_stack_exports.py # Type-safe CloudFormation export interface
    │   │       └── lambda_stack.py        # Lambda functions, layers, events
    │   │
    │   ├── tests/                    # Test utilities (inside the package)
    │   │   ├── conftest.py           # Shared pytest fixtures
    │   │   ├── helper.py             # run_unit_test / run_cov_test wrappers
    │   │   └── mock_aws.py           # Mock/real AWS test base class
    │   │
    │   └── vendor/                   # Vendored third-party utilities
    │       └── pytest_cov_helper.py  # Per-module coverage runner
    │
    ├── tests/                        # ── Unit tests (mocked, fast) ──
    │   ├── all.py                    # Run all with full-project coverage
    │   ├── lbd/                      # Lambda handler tests
    │   ├── config/                   # Config model tests
    │   └── cdk/                      # CDK synthesis smoke tests
    │
    ├── tests_int/                    # ── Integration tests (real AWS) ──
    │   ├── lbd/                      # Invoke deployed Lambda functions
    │   └── iac/                      # Verify CloudFormation exports
    │
    └── cdk/                          # ── CDK app entry point ──
        ├── cdk.json                  # CDK configuration
        └── cdk_app.py                # App synthesis script


Module Dependency Graph
------------------------------------------------------------------------------

Modules are organized in layers from most foundational (Layer 0) to
highest-level entry points (Layer 5).  Each layer only depends on layers
below it — **never sideways or upward**.

::

    Layer 5 ─ Entry Points
    │   cdk/cdk_app.py            synthesizes CDK stacks
    │   lambda_function.py        AWS Lambda runtime entry point
    │
    Layer 4 ─ CDK Infrastructure
    │   cdk/stack_enum.py         lazy stack registry
    │   cdk/stacks/infra_stack.py IAM resources
    │   cdk/stacks/lambda_stack.py Lambda + event sources
    │
    Layer 3 ─ Lambda Handlers
    │   lbd/base.py               Pydantic handler base classes
    │   lbd/hello.py              greeting handler
    │   lbd/s3sync.py             S3 copy handler
    │
    Layer 2 ─ Singleton Resource Access
    │   one/one_00_main.py        composed from mixins below
    │   one/one_01_config.py      runtime-aware config loading
    │   one/one_02_boto_ses.py    boto3 session management
    │   one/one_03_s3.py          S3 bucket/path conventions
    │   one/one_04_devops.py      build & deploy automation
    │
    Layer 1 ─ Configuration Models
    │   config/config_00_main.py  top-level Config (Pydantic)
    │   config/config_01_lbd_func.py   per-function LbdFunc model
    │   config/config_02_lbd_deploy.py deployment mixin
    │
    Layer 0 ─ Zero-dependency Foundations
        constants.py              magic strings (LATEST, LIVE, etc.)
        paths.py                  absolute path enumeration
        runtime.py                "am I in Lambda?" detection
        logger.py                 shared logger singleton
        lazy_imports.py           dev-only dependency guard


Key Design Patterns
------------------------------------------------------------------------------

The table below summarizes each pattern, where it lives, and where to find
the **why** explanation in the source code.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Pattern
     - Key Module
     - Why (see module docstring)
   * - Singleton + lazy loading
     - :mod:`cookiecutter_aws_lbd_demo.one`
     - Avoid import-time side effects, prevent circular imports
   * - Mixin composition with numbered files
     - :mod:`cookiecutter_aws_lbd_demo.one.one_00_main`
     - Separation of concerns, explicit dependency order
   * - ``@cached_property`` everywhere
     - :mod:`cookiecutter_aws_lbd_demo.one` (docstring)
     - Compute once on first access; better than ``__init__`` or ``@property``
   * - Runtime-aware config loading
     - :mod:`cookiecutter_aws_lbd_demo.one.one_01_config`
     - Lambda uses env vars from CDK; local uses ``.env`` files
   * - Pydantic Lambda handler (BaseInput/BaseOutput)
     - :mod:`cookiecutter_aws_lbd_demo.lbd.base`
     - Type-safe I/O validation with automatic serialization
   * - ``_config`` back-reference (PrivateAttr)
     - :mod:`cookiecutter_aws_lbd_demo.config.config_01_lbd_func`
     - Child needs parent for computed names; can't be a constructor arg
   * - Infra / Lambda stack separation
     - :mod:`cookiecutter_aws_lbd_demo.cdk.stacks.infra_stack`
     - Different change frequencies, blast-radius isolation
   * - ``StackEnum`` lazy registry
     - :mod:`cookiecutter_aws_lbd_demo.cdk.stack_enum`
     - Only synthesize stacks you access; IDE-friendly
   * - CloudFormation export interface
     - :mod:`cookiecutter_aws_lbd_demo.cdk.stacks.infra_stack_exports`
     - Type-safe, copy-pasteable cross-project resource access
   * - ``AWS_ACCOUNT_ALIAS`` baked at synth time
     - :mod:`cookiecutter_aws_lbd_demo.cdk.stacks.lambda_stack` (line ~88)
     - Avoids IAM API call in Lambda cold start (was causing timeouts)
   * - Lazy dev imports with ``MissingDependency``
     - :mod:`cookiecutter_aws_lbd_demo.lazy_imports`
     - Dev deps not in Lambda Layer; sentinel defers error to point of use
   * - ``api.py`` re-export convention
     - :mod:`cookiecutter_aws_lbd_demo.api`
     - Keep ``__init__.py`` import-free; explicit public surface
   * - Mock/real AWS test switch
     - :mod:`cookiecutter_aws_lbd_demo.tests.mock_aws`
     - One test class, two modes; moto for CI, real AWS for integration
   * - ``if __name__ == "__main__"`` test runner
     - :mod:`cookiecutter_aws_lbd_demo.tests.helper`
     - Run one file with per-module coverage; fast dev feedback
   * - Vendored utilities
     - :mod:`cookiecutter_aws_lbd_demo.vendor`
     - Tiny scripts not worth a PyPI dependency


The ``one`` Singleton — Central Nervous System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :mod:`~cookiecutter_aws_lbd_demo.one` subpackage is the most important
architectural concept.  It provides a single ``one`` instance that lazily
wires together config, AWS sessions, S3 paths, and DevOps operations:

.. literalinclude:: ../../../../cookiecutter_aws_lbd_demo/one/one_00_main.py
   :language: python
   :lines: 46-59
   :caption: one/one_00_main.py — the One class composed from mixins


The Lambda Handler Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every Lambda function follows the same structure: a Pydantic ``Input`` model
with a ``main()`` method, and a module-level ``lambda_handler``.

.. literalinclude:: ../../../../cookiecutter_aws_lbd_demo/lbd/hello.py
   :language: python
   :caption: lbd/hello.py — a minimal Lambda function implementation

All handlers are re-exported through a single entry point:

.. literalinclude:: ../../../../cookiecutter_aws_lbd_demo/lambda_function.py
   :language: python
   :lines: 23-24
   :caption: lambda_function.py — handler registry


How to Extend
------------------------------------------------------------------------------


Adding a New Lambda Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow these steps to add a new Lambda function (e.g., ``my_func``):

1. **Create the handler module** — ``cookiecutter_aws_lbd_demo/lbd/my_func.py``:

   .. code-block:: python

       from pydantic import Field
       from ..logger import logger
       from .base import BaseInput, BaseOutput


       class Output(BaseOutput):
           result: str = Field()


       class Input(BaseInput[Output]):
           param: str = Field()

           @logger.pretty_log()
           def main(self, context=None) -> Output:
               return Output(result=f"processed {self.param}")


       lambda_handler = Input.lambda_handler

2. **Register the handler** — add to
   ``cookiecutter_aws_lbd_demo/lambda_function.py``:

   .. code-block:: python

       from cookiecutter_aws_lbd_demo.lbd.my_func import lambda_handler as my_func_handler

3. **Add configuration** — add env vars to ``.env.shared``:

   .. code-block:: bash

       LBD_FUNC_MY_FUNC_SHORT_NAME="my_func"
       LBD_FUNC_MY_FUNC_HANDLER="my_func_handler"
       LBD_FUNC_MY_FUNC_TIMEOUT="10"
       LBD_FUNC_MY_FUNC_MEMORY="128"

4. **Add the config field** — in
   :mod:`~cookiecutter_aws_lbd_demo.config.config_00_main`:

   .. code-block:: python

       lbd_func_my_func: LbdFunc | None = Field()

5. **Load the config** — add to the ``else`` branch of
   :mod:`~cookiecutter_aws_lbd_demo.one.one_01_config` (``OneConfigMixin.config``):

   .. code-block:: python

       lbd_func_my_func = LbdFunc(
           short_name=os.environ["LBD_FUNC_MY_FUNC_SHORT_NAME"],
           handler=os.environ["LBD_FUNC_MY_FUNC_HANDLER"],
           timeout=int(os.environ["LBD_FUNC_MY_FUNC_TIMEOUT"]),
           memory=int(os.environ["LBD_FUNC_MY_FUNC_MEMORY"]),
           layers=[os.environ["LBD_FUNC_LAYER_VERSION"]],
       )

   And pass it to the ``Config(...)`` constructor, and add the ``_config``
   back-reference:

   .. code-block:: python

       config.lbd_func_my_func._config = config

6. **CDK will auto-discover** — the Lambda stack iterates
   ``config.lbd_func_mappings`` which auto-discovers all ``LbdFunc`` fields.
   No CDK changes needed unless the function needs custom event sources or
   IAM permissions.

7. **Write tests**:

   - ``tests/lbd/test_lbd_my_func.py`` — unit test with mocked services
   - ``tests_int/lbd/test_lbd_my_func.py`` — integration test against real AWS


Adding a New CDK Stack or Resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Adding a resource to an existing stack:**

Add a new numbered method (e.g., ``s03_create_sqs_queue``) to the
appropriate stack class and call it from ``__init__``.  Follow the section
numbering convention (``s01_``, ``s02_``, ``s03_``, …).

**Adding an entirely new stack:**

1. Create ``cookiecutter_aws_lbd_demo/cdk/stacks/my_stack.py``
2. Add a ``@cached_property`` to :mod:`~cookiecutter_aws_lbd_demo.cdk.stack_enum`:

   .. code-block:: python

       @cached_property
       def my_stack(self):
           from .stacks.my_stack import MyStack
           return MyStack(scope=self.app, one=one)

3. Access it in ``cdk/cdk_app.py``:

   .. code-block:: python

       _ = stack_enum.my_stack

**Adding a Step Function or other AWS resource:**

Step Functions, SQS queues, DynamoDB tables, etc. follow the same pattern —
create the constructs inside a stack method and wire them up.  For Step
Functions specifically:

1. Define the state machine in a new stack method (e.g.,
   ``s03_create_step_function``) or in a new stack if it's complex.
2. Grant the Lambda execution role permission to invoke the state machine
   (or vice versa) in the IAM section of ``infra_stack.py``.
3. If the Step Function needs to invoke Lambda functions, use
   ``config.lbd_func_mappings`` to get function names dynamically.

**Exporting resources for other projects:**

If other projects need to reference your new resource, add a ``CfnOutput``
in the stack and a corresponding ``@cached_property`` in
:mod:`~cookiecutter_aws_lbd_demo.cdk.stacks.infra_stack_exports`.  See that
module's docstring for the full extension guide.
