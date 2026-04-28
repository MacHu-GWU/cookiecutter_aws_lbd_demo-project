# -*- coding: utf-8 -*-

"""
Singleton Variable Access Subpackage (``one``)

**What:** A single ``one = One()`` instance that provides lazy-loaded access to
every shared resource the project needs — configuration, AWS sessions, S3 paths,
and DevOps automation.

**Why a singleton?**  In a Lambda function (and in local scripts), many
resources are expensive to create (boto sessions, config parsing) and should be
created at most once per process.  A module-level singleton with
``@cached_property`` attributes gives us:

- **Lazy initialization** — nothing is created until first use.  Importing
  ``from .one.api import one`` is free; the boto session is only built when
  ``one.boto_ses`` is first accessed.
- **No circular imports** — because initialization is deferred, the import
  graph stays acyclic even though config, boto, S3, and DevOps code all
  cross-reference each other.
- **Single source of truth** — every call site shares the same config and
  session instance, avoiding subtle bugs from duplicated state.

**File organization:** The ``One`` class is assembled from numbered mixin files
(``one_00_main.py``, ``one_01_config.py``, …).  See ``one_00_main.py`` module
docstring for why the mixin pattern and numbered naming convention are used.

**Usage**::

    from cookiecutter_aws_lbd_demo.one.api import one

    one.config          # lazy-loaded Config object
    one.boto_ses        # lazy-loaded boto3.Session
    one.s3dir_lambda    # lazy-loaded S3Path
"""
