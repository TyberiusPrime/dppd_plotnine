#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for dppd.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""

# import pytest
import sys

sys.path.append("src")

from plotnine.tests.conftest import (  # noqa:F401
    _setup,
    _teardown,  # noqa:F401
    pytest_assertrepr_compare,
)

_setup()
