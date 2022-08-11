import plotnine as p9
from dppd import register_verb
import pandas as pd
from patsy import EvalEnvironment
from . import geoms


# this establishes the p9-dppd support


@register_verb("p9", types=pd.DataFrame)
def p9_DataFrame(df, mapping=None):
    return p9.ggplot(mapping=mapping, data=df, environment=EvalEnvironment.capture(2))


never_map = set(["data", "stat", "position"])
other_args = set(['DEFAULT_AES'])

add_funcs = {}


def sensible_aes_order(required_aes):
    order = []
    if "x" in required_aes:
        order.append("x")
    if "y" in required_aes:
        order.append("y")
    for a in sorted(required_aes):
        if a != "x" and a != "y":
            order.append(a)
    return order





def iter_elements():
    for name in dir(p9):
        if "_" in name and name[: name.find("_")] in (
            "geom",
            "annotate",
            "annotation",
            "scale",
            "theme",
            "facet",
            "coord",
        ):
            cls = getattr(p9, name)
            yield (name, cls)
    yield ("theme", p9.theme)
    for name in dir(geoms):
        cls = getattr(geoms, name)
        yield (name, cls)


aliases = {
    "scale_y_continuous": ["syc"],
    "scale_x_continuous": ["sxc"],
}

for name, cls in iter_elements():

    if name in aliases:
        register_name = aliases[name] + [name]
    else:
        register_name = name

    @register_verb(register_name, types=p9.ggplot)
    def add_geom(plot, *args, cls=cls, **kwargs):
        if args and isinstance(args[0], dict):
            args = list(args)
            args[0] = p9.aes(**args[0])
        return plot + cls(*args, **kwargs)

    if name.startswith("geom"):
        add_name = "add" + name[name.find("_") :]
        cyberpunks = ["add_point", "add_line", "add_boxplot", "add_bar"]
        if add_name in cyberpunks:

            @register_verb(add_name, types=p9.ggplot, pass_dppd=True)
            def add_wrapped_add_geom(dppd, *args, add_name=add_name, **kwargs):
                if hasattr(dppd.df, "cyberpunked"):
                    return getattr(dppd, add_name + "_cyberpunk")(*args, **kwargs)
                else:
                    return getattr(dppd, "_" + add_name)(*args, **kwargs)

            add_name = "_" + add_name

        @register_verb(add_name, types=p9.ggplot)
        def add_add_geom(plot, *args, cls=cls, **kwargs):
            if len(args) > len(cls.REQUIRED_AES):
                raise ValueError(
                    "More position arguments then required aes were passed in. "
                    "Switch to keyword arguments to precisly define what you mean"
                )
            for k, v in zip(sensible_aes_order(cls.REQUIRED_AES), args):
                if not k in kwargs and not "_" + k in kwargs:
                    kwargs[k] = v
                else:
                    raise ValueError(
                        f"{k} specified twice, once per position and once per kwarg"
                    )
            mapped = {}
            non_mapped = {}
            other = {}
            for k, v in kwargs.items():
                if k in other_args:
                    other[k] = v
                elif k in never_map:
                    non_mapped[k] = v
                elif k.startswith("_"):
                    non_mapped[k[1:]] = v
                else:
                    mapped[k] = v

            if cls is p9.geom_bar and not "stat" in non_mapped:
                non_mapped["stat"] = p9.stat_identity()

            if "data" in kwargs and kwargs["data"] is None:  # explicitly set to None
                fake_data = {k: mapped[k] for k in cls.REQUIRED_AES if k in mapped}
                try:
                    data = pd.DataFrame(fake_data)
                except ValueError as e:
                    if "you must pass an index" in str(e):
                        data = pd.DataFrame(fake_data, index=[0])
                    else:
                        raise

                mapped = {k: k for k in cls.REQUIRED_AES if k in mapped}
                non_mapped["data"] = data

            geom = cls(p9.aes(**mapped), **non_mapped)
            if 'DEFAULT_AES' in other:
                geom.DEFAULT_AES = geom.DEFAULT_AES.copy()
                geom.DEFAULT_AES.update(other['DEFAULT_AES'])
            return plot + geom

        add_funcs[add_name] = add_add_geom


@register_verb(["save", "render"], types=p9.ggplot)
def save(plot, *args, **kwargs):
    """Save a plot.
    Arguments are drawn from the kwargs + the plot's .render_args
    (kwargs overwrite render_args).

    Optional new kw_arg is size, which may be one of A4/A5/A6,
    and replaces the width&height (use A4 for portrait, a4 for landscape...)"""

    if not "verbose" in kwargs:  # pragma: no cover
        kwargs["verbose"] = False
    else:  # pragma: no cover
        pass  # pragma: no cover
    if hasattr(plot, "render_args"):
        org = kwargs
        kwargs = {}
        kwargs.update(plot.render_args)
        kwargs.update(org)
    if "size" in kwargs:
        import re

        sizes = {
            1: (23.4, 33.1),
            2: (16.5, 24.4),
            3: (11.7, 16.5),
            4: (8.3, 11.7),
            5: (5.8, 8.3),
            6: (4.1, 5.8),
            7: (2.9, 4.1),
        }
        s = kwargs["size"]
        if not re.match("^A|a[1234567]", s):
            raise ValueError(
                "size must be one of A1..A7 (portrait) or a1..a7 (landscape)"
            )
        portrait = s[0] == "A"
        width, height = sizes[int(s[1])]
        if not portrait:
            height, width = width, height
        del kwargs["size"]
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["unit"] = "in"

    plot.save(*args, **kwargs)
    return plot


@register_verb("add_scatter", types=p9.ggplot, pass_dppd=True)
def add_scatter(dppd, *args, **kwargs):
    return dppd.add_point(*args, **kwargs)


@register_verb("title", types=p9.ggplot)
def add_title_p9(plot, title):
    return plot + p9.ggtitle(title)


@register_verb("xlab", types=p9.ggplot)
def add_xlab_p9(plot, xlab):
    return plot + p9.xlab(xlab)


@register_verb("ylab", types=p9.ggplot)
def add_ylab_p9(plot, ylab):
    return plot + p9.ylab(ylab)


@register_verb(["figure_size", "size", "fig_size"], types=p9.ggplot)
def add_figure_size(plot, w, h):
    return plot + p9.theme(figure_size=(w, h))
