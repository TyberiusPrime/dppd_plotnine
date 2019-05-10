from dppd import dppd
import pytest
from plotnine.data import mtcars
import dppd_plotnine  # noqa: F401

dp, X = dppd()


def test_annotation_strips(per_test_dir):
    actual = dp(mtcars).p9().theme_bw().annotation_stripes().add_scatter("cyl", "hp").pd
    assert actual == "test_annotation_strips"


def test_annotation_strips_coord_flip(per_test_dir):
    actual = (
        dp(mtcars)
        .p9()
        .theme_bw()
        .annotation_stripes()
        .add_scatter("cyl", "hp")
        .coord_flip()
        .pd
    )
    assert actual == "test_annotation_strips_coord_flip"


def test_annotation_strips_horiontal(per_test_dir):
    actual = (
        dp(mtcars)
        .categorize("cyl")
        .p9()
        .theme_bw()
        .annotation_stripes(direction="horizontal", fills=["#FF0000", "#00FF00"])
        .add_scatter("hp", "cyl")
        .pd
    )
    assert actual == "test_annotation_strips_horiontal"


def test_annotation_strips_horiontal_coord_flip(per_test_dir):
    actual = (
        dp(mtcars)
        .categorize("cyl")
        .p9()
        .theme_bw()
        .annotation_stripes(direction="horizontal", fills=["#FF0000", "#00FF00"])
        .add_scatter("hp", "cyl")
        .coord_flip()
        .pd
    )
    assert actual == "test_annotation_strips_horiontal_coord_flip"


def test_invalid_orientation_raises():
    with pytest.raises(ValueError):
        dp(mtcars).p9().theme_bw().annotation_stripes(direction="diagonal")
    dp(mtcars).p9().theme_bw().annotation_stripes(direction="vertical").pd
    dp(mtcars).p9().theme_bw().annotation_stripes(direction="horizontal").pd
