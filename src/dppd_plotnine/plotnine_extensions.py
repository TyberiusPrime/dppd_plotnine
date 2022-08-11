import plotnine as p9
from dppd import register_verb

# verbs that extend the normal p9 spectrum


def _change_theme(plot, what, t):
    # if plot.plot.theme is None:
    # plot.theme_grey()
    # plot.plot.theme +=
    return plot + p9.theme(**{what: t})


def _turn_axis_labels(plot, ax, angle, hjust, vjust, size, color):
    t = p9.themes.element_text(
        rotation=angle, ha=hjust, va=vjust, size=size, color=color
    )
    return _change_theme(plot, ax, t)


@register_verb(types=p9.ggplot)
def turn_x_axis_labels(
    plot, angle=90, hjust="center", vjust="top", size=None, color=None
):
    """
    Rotate X axis labels - by default 90 degrees.
    See :class:`plotnine.themes.element_text` for details.

    """
    return _turn_axis_labels(plot, "axis_text_x", angle, hjust, vjust, size, color)


@register_verb(types=p9.ggplot)
def turn_y_axis_labels(
    plot, angle=90, hjust="right", vjust="center", size=None, color=None
):
    """
    Rotate Y axis labels - by default 90 degrees.
    See :class:`plotnine.themes.element_text` for details.

    """
    return _turn_axis_labels(plot, "axis_text_y", angle, hjust, vjust, size, color)


@register_verb(types=p9.ggplot)
def hide_background(plot):
    """Hide the panel background"""
    return _change_theme(plot, "panel_background", p9.element_blank())


@register_verb(types=p9.ggplot)
def hide_x_axis_labels(plot):
    """Hide the labels on the X axis"""
    return _change_theme(plot, "axis_text_x", p9.element_blank())


@register_verb(types=p9.ggplot)
def hide_y_axis_labels(plot):
    """Hide the labels on the y axis"""
    return _change_theme(plot, "axis_text_y", p9.element_blank())


@register_verb(types=p9.ggplot)
def hide_axis_ticks(plot):
    """Hide the ticks on both axis"""
    return _change_theme(plot, "axis_ticks", p9.element_blank())


@register_verb(types=p9.ggplot)
def hide_x_axis_ticks(plot):
    """Hide the ticks on the X axis"""
    return _change_theme(plot, "axis_ticks_major_x", p9.element_blank())


@register_verb(types=p9.ggplot)
def hide_y_axis_ticks(plot):
    """Hide the ticks on the Y axis"""
    return _change_theme(plot, "axis_ticks_major_y", p9.element_blank())


@register_verb(types=p9.ggplot)
def hide_x_axis_title(plot):
    """Hide the title of the X axis"""
    return _change_theme(plot, "axis_title_x", p9.element_blank())


@register_verb(types=p9.ggplot)
def hide_y_axis_title(plot):
    """Hide the title of the Y axis"""
    return _change_theme(plot, "axis_title_y", p9.element_blank())


@register_verb(types=p9.ggplot)
def hide_facet_labels(plot):
    """Hide the facet labels"""
    _change_theme(plot, "strip_background", p9.element_blank())
    return _change_theme(plot, "strip_text_x", p9.element_blank())

@register_verb(types=p9.ggplot)
def hide_legend_title(plot):
    """Hide the legend label"""
    return _change_theme(plot, "legend_title", p9.element_blank())


_many_cat_colors = [
    "#1C86EE",
    "#E31A1C",  # red
    "#008B00",
    "#6A3D9A",  # purple
    "#FF7F00",  # orange
    "#4D4D4D",
    "#FFD700",
    "#7EC0EE",
    "#FB9A99",  # lt pink
    "#90EE90",
    "#0000FF",
    "#FDBF6F",  # lt orange
    "#B3B3B3",
    "#EEE685",
    "#B03060",
    "#FF83FA",
    "#FF1493",
    "#0000FF",
    "#36648B",
    "#00CED1",
    "#00FF00",
    "#8B8B00",
    "#CDCD00",
    "#A52A2A",
]


@register_verb(types=p9.ggplot)
def scale_fill_many_categories(plot, offset=0, **kwargs):
    """A fill scale with some 23 fairly distinguishable colors"""
    return plot + p9.scale_fill_manual(
        (_many_cat_colors + _many_cat_colors)[offset : offset + len(_many_cat_colors)],
        **kwargs
    )


@register_verb(types=p9.ggplot)
def scale_color_many_categories(plot, offset=0, **kwargs):
    """A color scale with some 23 fairly distinguishable colors"""
    return plot + p9.scale_color_manual(
        (_many_cat_colors + _many_cat_colors)[offset : offset + len(_many_cat_colors)],
        **kwargs
    )


@register_verb(types=p9.ggplot)
def aes(_plot, *args, **kwargs):  # pragma: no cover
    return p9.aes(*args, **kwargs)


@register_verb(types=p9.ggplot)
def reverse_transform(_plot, trans):
    from mizani.transforms import trans_new
    from mizani.transforms import gettrans
    import numpy as np

    """Take a transform and make it go from high to low
    instead of low to high
    """

    def inverse_breaks(limits):
        return trans.breaks(tuple(sorted(limits)))

    def inverse_minor_breaks(major, limits):
        return trans.minor_breaks(major, tuple(sorted(limits)))

    if isinstance(trans, str):
        trans = gettrans(trans)
    if trans.__class__.__name__ != "type":
        name = "-" + trans.__class__.__name__
    else:
        name = "-" + trans.__name__  # pragma: no cover
    if name.endswith("_trans"):
        name = name[: -len("_trans")]
    return trans_new(
        name,
        lambda x: -1 * trans.transform(x),
        lambda x: trans.inverse(np.array(x) * -1),
        breaks=inverse_breaks,
        minor_breaks=inverse_minor_breaks,
        _format=trans.format,
        domain=trans.domain,
    )


@register_verb("render_args", types=p9.ggplot)
def render_args(plot, **render_args):
    """preregister arguments that will be used on save"""
    plot.render_args = render_args
    return plot


@register_verb("add_cummulative", types=p9.ggplot)
def add_cummulative(plot, x_column, ascending=True, percent=False, percentile=1.0):
    """Add a line showing cumulative % of data <= x.
        if you specify a percentile, all data at the extreme range is dropped


    """
    import numpy as np
    import pandas as pd
    import itertools

    total = 0
    current = 0
    column_data = plot.data[x_column].copy()  # explicit copy!
    column_data = column_data[~np.isnan(column_data)]
    column_data = np.sort(column_data)
    total = float(len(column_data))
    real_total = total
    if not ascending:
        column_data = column_data[::-1]  # numpy.reverse(column_data)
    if percentile != 1.0:
        if ascending:
            maximum = np.max(column_data)
        else:
            maximum = np.min(column_data)
        total = float(total * percentile)
        if total > 0:
            column_data = column_data[:total]
            offset = real_total - total
        else:
            column_data = column_data[total:]
            offset = 2 * abs(total)
    else:
        offset = 0
    x_values = []
    y_values = []
    if percent:
        current = 100.0
    else:
        current = total
    for value, group in itertools.groupby(column_data):
        x_values.append(value)
        y_values.append(current + offset)
        if percent:
            current -= len(list(group)) / total
        else:
            current -= len(list(group))
        # y_values.append(current)
    data = pd.DataFrame(
        {x_column: x_values, ("%" if percent else "#") + " <=": y_values}
    )
    out_plot = plot
    if percentile > 0:
        out_plot = out_plot + p9.scale_x_continuous(
            limits=[0, real_total if not percent else 100]
        )
    out_plot = out_plot + p9.geom_line(
        p9.aes(x_column, ("%" if percent else "#") + " <="), data=data
    )
    if percentile != 1.0:
        out_plot = out_plot + p9.title(
            "showing only %.2f percentile, extreme was %.2f" % (percentile, maximum)
        )
    return out_plot


@register_verb("hide_legend", types=p9.ggplot)
def hide_legend(plot):
    """Hide plot legend - whether you have manually defined a scale or not"""
    import types

    def my_compute_aesthetics(self, p):
        print("my_compute_aesthetics", type(p))
        res = self._org_compute_aesthetics(p)
        for s in p.scales:
            s.guide = False
        return res

    plot.layers._org_compute_aesthetics = plot.layers.compute_aesthetics
    # advanced monkey patching for the win!
    plot.layers.compute_aesthetics = types.MethodType(
        my_compute_aesthetics, plot.layers
    )
    return plot

@register_verb('sc10', types=p9.ggplot)
def sc10(plot):
    return plot + p9.scale_x_continuous(trans='log10') + p9.scale_y_continuous(trans='log10')

@register_verb("sxc10", types=p9.ggplot)
def sxc10(plot, *args, **kwargs):
    """scale_x_continuous(trans='log10',...)"""
    if not "trans" in kwargs:
        kwargs["trans"] = "log10"
    return plot + p9.scale_x_continuous(*args, **kwargs)


@register_verb("syc10", types=p9.ggplot)
def syc10(plot, *args, **kwargs):
    """scale_y_continuous(trans='log10',...)"""
    if not "trans" in kwargs:
        kwargs["trans"] = "log10"
    return plot + p9.scale_y_continuous(*args, **kwargs)


@register_verb("sxc2", types=p9.ggplot)
def sxc2(plot, *args, **kwargs):
    """scale_x_continuous(trans='log2',...)"""
    if not "trans" in kwargs:
        kwargs["trans"] = "log2"
    return plot + p9.scale_x_continuous(*args, **kwargs)


@register_verb("syc2", types=p9.ggplot)
def syc2(plot, *args, **kwargs):
    """scale_y_continuous(trans='log2',...)"""
    if not "trans" in kwargs:
        kwargs["trans"] = "log2"
    return plot + p9.scale_y_continuous(*args, **kwargs)


@register_verb("theme_cyberpunk", types=p9.ggplot)
def theme_cyberpunk(plot, theme_kwargs={}):
    theme = {
        "panel_background": p9.element_rect(fill="#212946"),
        "plot_background": p9.element_rect(fill="#212946"),
        "text": p9.element_text(color="#E5E5E5"),
        "legend_background": p9.element_rect(fill="#212946"),
        "legend_key": p9.element_rect(fill="#212946"),
        "panel_grid_major": p9.element_line(color="#5A6489"),
        "panel_grid_minor": p9.element_line(color="#5A6489"),
        "axis_ticks_major": p9.element_line(color="#5A6489"),
        "axis_ticks_minor": p9.element_line(color="#5A6489"),
    }
    theme.update(theme_kwargs)
    return plot + p9.theme(**theme)


cyberpunk_colors = [
    "#08F7FE",
    "#FE53BB",
    "#F5D300",
    "#00ff41",
    "red",
    "#9467bd",
]


@register_verb("scale_color_cyberpunk", types=p9.ggplot)
def scale_color_cyberpunk(plot, **kwargs):
    return plot + p9.scale_color_manual(cyberpunk_colors, **kwargs)


@register_verb("scale_fill_cyberpunk", types=p9.ggplot)
def scale_fill_cyberpunk(plot, **kwargs):
    return plot + p9.scale_fill_manual(cyberpunk_colors, **kwargs)


@register_verb("cyberpunk", types=p9.ggplot, pass_dppd=True)
def cyberpunk(dppd):
    """Turn this plot into a cyberpunk styled plot with theme and glowing figures"""
    res = dppd.theme_cyberpunk().scale_color_cyberpunk().scale_fill_cyberpunk()
    res.df.cyberpunked = True
    # res.add_scatter = res.add_scatter_cyberpunk
    # res.add_line = res.add_line_cyberpunk
    return res


@register_verb(
    ["add_scatter_cyberpunk", "add_point_cyberpunk"], types=p9.ggplot, pass_dppd=True
)
def add_scatter_cyberpunk(dppd, *args, **kwargs):
    kwargs_glow = kwargs.copy()
    if "size" in kwargs:
        kwargs_glow["size"] = kwargs["size"] + " + 3"
    elif "_size" in kwargs:
        kwargs_glow["_size"] = kwargs["_size"] + 3
    else:
        kwargs["_size"] = 2
        kwargs_glow["_size"] = 5
    kwargs_glow["_alpha"] = 0.1
    res = dppd._add_point(*args, **kwargs_glow)
    return res._add_point(*args, **kwargs, DEFAULT_AES={"color": "white"})


@register_verb("add_line_cyberpunk", types=p9.ggplot, pass_dppd=True)
def add_line_cyberpunk(dppd, *args, **kwargs):
    kwargs_glow1 = kwargs.copy()
    kwargs_glow2 = kwargs.copy()
    if "size" in kwargs:
        kwargs_glow1["size"] = kwargs["size"] + " + 1"
        kwargs_glow2["size"] = kwargs["size"] + " + 4"
    elif "_size" in kwargs:
        kwargs_glow1["_size"] = kwargs["_size"] + 1
        kwargs_glow2["_size"] = kwargs["_size"] + 4
    else:
        kwargs["_size"] = 0.5
        kwargs_glow1["_size"] = kwargs["_size"] + 1
        kwargs_glow2["_size"] = kwargs["_size"] + 4
    kwargs_glow1["_alpha"] = 0.3
    kwargs_glow2["_alpha"] = 0.15
    if not "color" in kwargs and not "_color" in kwargs:
        kwargs["color"] = '"a"'
        kwargs_glow1["color"] = '"a"'
        kwargs_glow2["color"] = '"a"'
        kwargs["_show_legend"] = False
        kwargs_glow1["_show_legend"] = False
        kwargs_glow2["_show_legend"] = False
    res = dppd._add_line(*args, **kwargs_glow2)
    res = res._add_line(*args, **kwargs_glow1)
    return res._add_line(*args, **kwargs, DEFAULT_AES={"color": "white"})


@register_verb("add_boxplot_cyberpunk", types=p9.ggplot, pass_dppd=True)
def add_boxplot_cyberpunk(dppd, *args, **kwargs):
    if not "_outlier_size" in kwargs:
        kwargs["_outlier_size"] = 1.5
    if not "fill" in kwargs and not "_fill" in kwargs:
        kwargs["_fill"] = None
    kwargs_glow1 = kwargs.copy()
    kwargs_glow1["_outlier_size"] = kwargs["_outlier_size"] + 3
    kwargs_glow1["_outlier_alpha"] = 0.1
    kwargs_glow1["_size"] = 3
    kwargs_glow1["_alpha"] = 0.1
    kwargs["_outlier_size"] = 1.5
    res = dppd._add_boxplot(*args, **kwargs_glow1)
    return res._add_boxplot(*args, **kwargs, DEFAULT_AES={'color': 'white'})


@register_verb("add_bar_cyberpunk", types=p9.ggplot, pass_dppd=True)
def add_bar_cyberpunk(dppd, *args, **kwargs):
    if not "_size" in kwargs:
        kwargs["_size"] = 0.5
    kwargs_glow1 = kwargs.copy()
    if not "fill" in kwargs and not "_fill" in kwargs:
        kwargs_glow1["_fill"] = "blue"
        kwargs["_fill"] = None
    kwargs_glow1["_alpha"] = 0.1
    kwargs_glow1["_size"] = kwargs["_size"] + 2.5
    res = dppd._add_bar(*args, **kwargs_glow1)
    return res._add_bar(*args, **kwargs, DEFAULT_AES={'color': 'white'})
