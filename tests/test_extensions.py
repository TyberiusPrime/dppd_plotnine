from dppd import dppd
import plotnine as p9
import dppd_plotnine  # noqa: F401
from plotnine.data import mtcars

dp, X = dppd()


def test_hide_background():
    actual = dp(mtcars).head(1).p9().add_point("mpg", "hp").hide_background().pd
    assert actual == "test_hide_background"


def test_hide_x_axis_labels():
    actual = dp(mtcars).head(1).p9().add_point("mpg", "hp").hide_x_axis_labels().pd
    assert actual == "test_hide_x_axis_labels"


def test_hide_x_axis_title():
    actual = dp(mtcars).head(1).p9().add_point("mpg", "hp").hide_x_axis_title().pd
    assert actual == "test_hide_x_axis_title"


def test_hide_y_axis_labels():
    actual = dp(mtcars).head(1).p9().add_point("mpg", "hp").hide_y_axis_labels().pd
    assert actual == "test_hide_y_axis_labels"


def test_hide_y_axis_title():
    actual = dp(mtcars).head(1).p9().add_point("mpg", "hp").hide_y_axis_title().pd
    assert actual == "test_hide_y_axis_title"


def test_hide_axis_ticks():
    actual = dp(mtcars).head(1).p9().add_point("mpg", "hp").hide_axis_ticks().pd
    assert actual == "test_hide_axis_ticks"


def test_hide_axis_ticks_x():
    actual = dp(mtcars).head(1).p9().add_point("mpg", "hp").hide_axis_ticks_x().pd
    assert actual == "test_hide_axis_ticks_x"


def test_hide_axis_ticks_y():
    actual = dp(mtcars).head(1).p9().add_point("mpg", "hp").hide_axis_ticks_y().pd
    assert actual == "test_hide_axis_ticks_y"


def test_hide_facet_labels():
    actual = (
        dp(mtcars)
        .head(5)
        .p9()
        .add_point("mpg", "hp")
        .facet_wrap("cyl")
        .hide_facet_labels()
        .pd
    )
    assert actual == "test_hide_facet_labels"


def test_scale_fill_many_categories():
    actual = (
        dp(mtcars)
        .head(5)
        .categorize("cyl")
        .p9()
        .add_bar("cyl", stat=p9.stat_count, fill="cyl")
        .scale_fill_many_categories()
        .pd
    )
    assert actual == "test_scale_fill_many_categories"


def test_scale_color_many_categories():
    actual = (
        dp(mtcars)
        .head(5)
        .categorize("cyl")
        .p9()
        .add_point("mpg", "hp", color="cyl")
        .scale_color_many_categories()
        .pd
    )
    assert actual == "test_scale_color_many_categories"


def test_turn_x_axis_labels():
    actual = (dp(mtcars).head(1).p9().add_point("mpg", "hp").turn_x_axis_labels()).pd
    assert actual == "test_turn_x_axis_labels"


def test_turn_y_axis_labels():
    actual = (dp(mtcars).head(1).p9().add_point("mpg", "hp").turn_y_axis_labels()).pd
    assert actual == "test_turn_y_axis_labels"


def test_reverse_transform():
    actual = (
        dp(mtcars)
        .head(10)
        .p9()
        .add_point("mpg", "hp")
        .scale_y_continuous(trans=dp.reverse_transform("log2"))
        .pd
    )
    assert actual == "test_reverse_transform"
