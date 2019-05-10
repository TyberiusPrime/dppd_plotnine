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
def hide_axis_ticks_x(plot):
    """Hide the ticks on the X axis"""
    return _change_theme(plot, "axis_ticks_major_x", p9.element_blank())


@register_verb(types=p9.ggplot)
def hide_axis_ticks_y(plot):
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
    "EEE685",
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
