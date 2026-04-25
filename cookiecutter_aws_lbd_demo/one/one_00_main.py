# -*- coding: utf-8 -*-

"""
Core singleton class combining all mixin functionality for centralized resource access.

This module provides the main One class that aggregates all specialized mixin functionality
into a single entry point, enabling lazy-loaded access to configuration, AWS services,
DevOps operations, and documentation generation through a unified singleton interface.
"""

try:
    from pywf_internal_proprietary.api import PyWf
except ImportError:  # pragma: no cover
    pass
from ..runtime import runtime

from .one_01_config import OneConfigMixin
from .one_02_boto_ses import OneBotoSesMixin


class One(
    OneConfigMixin,
    OneBotoSesMixin,
):  # pragma: no cover
    """
    Main singleton class providing unified access to all application resources and services.
    """

    runtime = runtime


one = One()
