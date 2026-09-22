from plotnine.data import mtcars
import dppd
import plotnine as p9
import numpy as np
import dppd_plotnine

dp, X = dppd.dppd()
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
        data=dp(X.data).groupby("cyl").summarize(("kwh", np.median, "kwh_median")).pd,
    )
    .scale_color_manual(["red", "blue", "purple"])  # after pd, X is what it was before
    .save("index.png")
)
