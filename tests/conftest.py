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
import os
import shutil
import pytest
from pathlib import Path

sys.path.append("src")

from plotnine.tests.conftest import (  # noqa:F401
    _setup,
    _teardown,  # noqa:F401
    pytest_assertrepr_compare,
)

_setup()


@pytest.fixture
def per_test_dir(request):
    import sys

    if request.cls is None:
        target_path = Path(request.fspath).parent / "run" / ("." + request.node.name)
    else:
        target_path = (
            Path(request.fspath).parent
            / "run"
            / (request.cls.__name__ + "." + request.node.name)
        )
    if target_path.exists():  # pragma: no cover
        shutil.rmtree(target_path)
    target_path = target_path.absolute()
    target_path.mkdir(parents=True)
    old_dir = Path(os.getcwd()).absolute()
    try:

        def np():
            return target_path

        def finalize():
            if hasattr(request.node, "rep_setup"):

                if request.node.rep_setup.passed and (
                    request.node.rep_call.passed
                    or request.node.rep_call.outcome == "skipped"
                ):
                    try:
                        if "--profile" not in sys.argv:
                            shutil.rmtree(target_path)
                    except OSError:  # pragma: no cover
                        pass

        request.addfinalizer(finalize)
        yield np()
    finally:
        os.chdir(old_dir)
