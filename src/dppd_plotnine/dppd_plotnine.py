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


for name, cls in iter_elements():

    @register_verb(name, types=p9.ggplot)
    def add_geom(plot, *args, cls=cls, **kwargs):
        return plot + cls(*args, **kwargs)

    if name.startswith("geom"):
        add_name = "add" + name[name.find("_") :]

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
            for k, v in kwargs.items():
                if k in never_map:
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

            return plot + cls(mapped, **non_mapped)

        add_funcs[add_name] = add_add_geom


@register_verb(["save", "render"], types=p9.ggplot)
def save(plot, *args, **kwargs):
    if not "verbose" in kwargs:  # pragma: no cover
        kwargs["verbose"] = False
    else:  # pragma: no cover
        pass  # pragma: no cover
    if hasattr(plot, "render_args"):
        org = kwargs
        kwargs = {}
        kwargs.update(plot.render_args)
        kwargs.update(org)
    plot.save(*args, **kwargs)
    return plot


@register_verb("add_scatter", types=p9.ggplot)
def add_scatter(plot, *args, **kwargs):
    return add_funcs["add_point"](plot, *args, **kwargs)


@register_verb("title", types=p9.ggplot)
def add_title_p9(plot, title):
    return plot + p9.ggtitle(title)


@register_verb("xlab", types=p9.ggplot)
def add_xlab_p9(plot, xlab):
    return plot + p9.xlab(xlab)


@register_verb("ylab", types=p9.ggplot)
def add_ylab_p9(plot, ylab):
    return plot + p9.ylab(ylab)
