import pytest
import os
import inspect
import locale
import shutil
import types
import warnings
from copy import deepcopy
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.testing.compare import compare_images

from plotnine import ggplot, theme

TOLERANCE = 2  # Default tolerance for the tests
DPI = 72  # Default DPI for the tests

# This partial theme modifies all themes that are used in
# the test. It is limited to setting the size of the test
# images Should a test require a larger or smaller figure
# size, the dpi or aspect_ratio should be modified.
test_theme = theme(figure_size=(640 / DPI, 480 / DPI), dpi=DPI)

tests_dir = Path(__file__).parent
baseline_images_dir = tests_dir / "baseline_images"
result_images_dir = tests_dir / "result_images"

if not baseline_images_dir.exists():
    raise OSError(
        "The baseline image directory does not exist. "
        "This is most likely because the test data is not installed. "
        "You may need to install plotnine from source to get the "
        "test data."
    )


def raise_no_baseline_image(filename: str):
    raise Exception(f"Baseline image {filename} is missing")


def ggplot_equals(plot: ggplot, name: str) -> bool:
    """
    Compare ggplot object to image determined by `right`

    Parameters
    ----------
    plot :
        ggplot object
    name :
        Identifier for the test image

    This function is meant to monkey patch ggplot.__eq__
    so that tests can use the `assert` statement.
    """
    test_file = inspect.stack()[1][1]
    filenames = make_test_image_filenames(name, test_file)
    # Save the figure before testing whether the original image
    # actually exists. This makes creating new tests much easier,
    # as the result image can afterwards just be copied.
    plot += test_theme
    with _test_cleanup():
        plot.save(filenames.result, verbose=False)

    if filenames.baseline.exists():
        shutil.copyfile(filenames.baseline, filenames.expected)
    else:
        # Putting the exception in short function makes for
        #  short pytest error messages
        raise_no_baseline_image(filenames.baseline)

    err = compare_images(
        filenames.expected, filenames.result, TOLERANCE, in_decorator=True
    )
    plot._err = err  # For the pytest error message
    return not err


ggplot.__eq__ = ggplot_equals


def draw_test(self):
    """
    Try drawing the ggplot object

    Parameters
    ----------
    self : ggplot
        ggplot object

    This function is meant to monkey patch ggplot.draw_test
    so that tests can draw and not care about cleaning up
    the MPL figure.
    """
    with _test_cleanup():
        self.draw()


ggplot.draw_test = draw_test


def build_test(self):
    """
    Try building the ggplot object

    Parameters
    ----------
    self : ggplot
        ggplot object

    This function is meant to monkey patch ggplot.build_test
    so that tests can build a plot and inspect the side effects
    on the plot object.
    """
    self = deepcopy(self)
    self._build()
    return self


ggplot.build_test = build_test


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, ggplot) and isinstance(right, str) and op == "==":
        msg = "images not close: {actual:s} vs. {expected:s} " "(RMS {rms:.2f})".format(
            **left._err
        )
        return [msg]


def make_test_image_filenames(name, test_file):
    """
    Create filenames for testing

    Parameters
    ----------
    name : str
        An identifier for the specific test. This will make-up
        part of the filenames.
    test_file : str
        Full path of the test file. This will determine the
        directory structure

    Returns
    -------
    out : types.SimpleNamespace
        Object with 3 attributes to store the generated filenames

            - result
            - baseline
            - expected

        `result`, is the filename for the image generated by the test.
        `baseline`, is the filename for the baseline image to which
        the result will be compared.
        `expected`, is the filename to the copy of the baseline that
        will be stored in the same directory as the result image.
        Creating a copy make comparison easier.
    """
    name = Path(name).with_suffix(".png")
    expected_name = f"{name.stem}-expected{name.suffix}"
    subdir = Path(test_file).stem
    filenames = types.SimpleNamespace(
        baseline=baseline_images_dir / subdir / name,
        result=result_images_dir / subdir / name,
        expected=result_images_dir / subdir / expected_name,
    )
    filenames.result.parent.mkdir(parents=True, exist_ok=True)
    return filenames


class _test_cleanup:
    def __enter__(self):
        # The baseline images are created in this locale, so we should use
        # it during all of the tests.
        try:
            locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, "English_United States.1252")
            except locale.Error:
                warnings.warn(
                    "Could not set locale to English/United States. "
                    "Some date-related tests may fail"
                )

        # make sure we don't carry over bad plots from former tests
        plt.close("all")
        n_figs = len(plt.get_fignums())
        msg = (
            f"No. of open figs: {n_figs}. Make sure the "
            "figures from the previous tests are cleaned up."
        )
        assert n_figs == 0, msg

        mpl.use("Agg")
        # These settings *must* be hardcoded for running the comparison
        # tests
        mpl.rcdefaults()  # Start with all defaults
        mpl.rcParams["text.hinting"] = "auto"
        mpl.rcParams["text.antialiased"] = True
        mpl.rcParams["text.hinting_factor"] = 8
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        plt.close("all")
        warnings.resetwarnings()


def layer_data(p, i=0):
    """
    Return layer information used to draw the plot

    Parameters
    ----------
    p : ggplot
        ggplot object
    i : int
        Layer number

    Returns
    -------
    out : dataframe
        Layer information
    """
    p = deepcopy(p)
    p._build()
    return p.layers.data[i]


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
