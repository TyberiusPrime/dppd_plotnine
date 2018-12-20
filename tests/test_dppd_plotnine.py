import numpy as np
import pandas as pd
import pytest
from dppd import dppd
import plotnine as p9
import dppd_plotnine  # noqa: F401
from plotnine.data import mtcars

dp, X = dppd()


def test_simple():
    actual = dp(mtcars).p9().geom_point({"x": "cyl", "y": "hp"}).pd
    assert actual == "test_simple"


def test_scale():
    actual = (
        dp(mtcars)
        .p9()
        .geom_point({"x": "cyl", "y": "hp"})
        .scale_y_continuous(trans="log10")
        .pd
    )
    assert actual == "test_scale"


def test_simple_add():
    actual = dp(mtcars).p9().add_point(x="cyl", y="hp").pd
    assert actual == "test_simple_add"


def test_more_than_the_number_of_required_aes_raises():
    with pytest.raises(ValueError):
        dp(mtcars).p9().add_point("mpg", "hp", "cyl").scale_color_brewer().pd


def test_unmapped():
    actual = dp(mtcars).p9().add_point(x="mpg", y="hp", _color="blue").pd
    assert actual == "test_unmapped"


def test_hline():
    actual = (
        dp(mtcars)
        .p9()
        .add_point(x="mpg", y="hp", _color="blue")
        .add_hline(200, _color="red")
        .pd
    )
    assert actual == "test_hline"


def test_spec_by_position_and_kwarg_raises():
    with pytest.raises(ValueError):
        (
            dp(pd.DataFrame({"x": [1, 2], "y": [2, 2]}))
            .p9()
            .add_crossbar("x", "y", "y", "y", ymin="y")
        )


def test_broken_data_mapping_raises_pandas_error():
    with pytest.raises(ValueError):
        (
            dp(pd.DataFrame({"x": [1, 2], "y": [2, 1.5]}))
            .p9()
            .add_point(x={"1": "shu"}, y=["4"], data=None)
            .pd
        )


def test_default_order():
    actual = (
        dp(pd.DataFrame({"x": [1, 2], "y": [2, 1.5]}))
        .p9()
        .add_crossbar("x", "y", "y-1", "y+.5")
        .pd
    )
    assert actual == "test_default_order"


def test_passing_in_lists():
    actual = dp(pd.DataFrame({"y": [2, 1.5]})).p9().add_point(["a", "b"], "y").pd
    assert actual == "test_passing_in_lists"


def test_passing_in_lists_unmapped():
    actual = (
        dp(pd.DataFrame({"x": ["a", "b"], "y": [2, 1.5]}))
        .p9()
        .add_point(x="x", y="y")
        .add_point(_x=[0.5, 0.8], y="y")
        .pd
    )
    assert actual == "test_unmapped_list"


def test_passing_in_scalar():
    actual = dp(pd.DataFrame({"y": [2, 1.5]})).p9().add_point('"a"', "y").pd
    assert actual == "test_passing_in_scalar"


def test_expression_vs_column():
    actual = (
        dp(pd.DataFrame({"x": [1, 2], "x*5": [0, 1], "y": [2, 1.5]}))
        .p9()
        .add_point("x*5", "y")
        .pd
    )
    assert actual == "test_expression_vs_column"


def test_expression_outside_variables():
    def times_two(x):
        return x * 2

    actual = (
        dp(pd.DataFrame({"x": [1, 2], "y": [2, 1.5]}))
        .p9()
        .add_point("times_two(x)", "y")
        .pd
    )
    assert actual == "test_expression_outside_variables"


def test_stat_count():
    actual = (
        dp(pd.DataFrame({"x": ["a", "a", "b"]}))
        .p9()
        .add_bar("x", y="stat(count)", stat=p9.stat_count())
        .pd
    )
    assert actual == "test_stat_count"


def test_bar_identity_stat_default():
    actual = (
        dp(pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})).p9().add_bar("x", y="y").pd
    )
    assert actual == "test_bar_identity_stat_default"


def test_chained():
    dp, X = dppd()  # for the X == None to work, we need a fresh Dppd
    actual = (
        dp(mtcars)
        .assign(kwh=X.hp * 0.74)
        .p9()
        .add_point(
            "cyl",
            "kwh",
            color="cyl",
            position=p9.position_jitter(height=0, random_state=500),
        )
        .add_errorbar(
            x="cyl",
            y="kwh_median",
            ymin="kwh_median",
            ymax="kwh_median",
            data=dp(X.data)
            .groupby("cyl")
            .summarize(("kwh", np.median, "kwh_median"))
            .pd,
        )
    ).pd
    assert X == None  # noqaE711
    assert actual == "test_chained"


def test_mapped_data_as_list():
    actual = dp(mtcars).p9().add_point(x=[1, 2, 3], y=[3, 2, 1], data=None).pd
    assert actual == "test_mapped_data_as_list"


def test_mapped_data_as_list_mixing_unmapped():
    actual = (
        dp(mtcars)
        .p9()
        .add_point(x=[1, 2, 3], y=[3, 2, 1], data=None, _color=["red", "blue", "green"])
        .pd
    )
    assert actual == "test_mapped_data_as_list_unmapped"


def test_mapped_data_as_list_mixing_unmapped_scalar():
    actual = (
        dp(mtcars).p9().add_point(x=[1, 2, 3], y=[3, 2, 1], data=None, _color="red").pd
    )
    assert actual == "test_mapped_data_as_list_mixing_unmapped_scalar"


def test_mapped_data_as_all_scalar():
    actual = dp(mtcars).p9().add_point(x=1, y=1, data=None, _color="red").pd
    assert actual == "test_mapped_data_as_all_scalar"


def test_theme_bw():
    actual = dp(mtcars).p9().add_point(x=1, y=1, data=None, _color="red").theme_bw().pd
    assert actual == "test_theme_bw"


def test_scatter():
    actual = dp(mtcars).p9().add_scatter(x=1, y=1, data=None).pd
    assert actual == "test_scatter"


def test_title():
    actual = (
        dp(mtcars)
        .p9()
        .add_scatter(x=1, y=1, data=None)
        .title("hello")
        .xlab("world")
        .ylab("today")
        .pd
    )
    assert actual == "test_title"


def test_save_is_non_verbose(capsys):
    import tempfile

    tf = tempfile.NamedTemporaryFile(suffix=".png")
    p = dp(mtcars).p9().add_point(x=1, y=1, data=None, _color="red").save(tf.name).pd
    assert isinstance(p, p9.ggplot)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_facet_wrap():
    actual = dp(mtcars).p9().add_scatter("hp", "cyl").facet_wrap("cyl").pd
    assert actual == "test_facet_wrap"


def test_coord_flip():
    actual = (
        dp(mtcars)
        .p9()
        .add_bar("cyl", y="hp", stat=p9.stat_summary(fun_y=np.mean))
        .coord_flip()
        .pd
    )
    assert actual == "test_coord_flip"


def test_create_doc_image():
    with pytest.warns(None) as record:
        (
            dp(mtcars)
            .assign(kwh=X.hp * 0.74)
            .categorize("cyl")
            .p9()
            .add_point(
                "cyl",
                "kwh",
                color="cyl",
                position=p9.position_jitter(height=0, random_state=500),
            )
            .add_errorbar(
                x="cyl",
                y="kwh_median",
                ymin="kwh_median",
                ymax="kwh_median",
                data=dp(X.data)
                .groupby("cyl")
                .summarize(("kwh", np.median, "kwh_median"))
                .pd,
            )
            .scale_color_manual(
                ["red", "blue", "purple"]
            )  # after pd, X is what it was before
            .save("docs/_static/index.png")
        )
        for k in record:
            assert k.category == PendingDeprecationWarning
