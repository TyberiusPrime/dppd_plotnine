# dppd_plotnine

| Build status: | [![Build Status](https://travis-ci.com/TyberiusPrime/dppd_plotnine.svg?branch=master)](https://travis-ci.com/TyberiusPrime/dppd_plotnine)|
|---------------|-----------------------------------------------------------------------------|
| Documentation | https://dppd_plotnine.readthedocs.io/en/latest/

dppd_plotnine combines the power of
[plotnine](https://plotnine.readthedocs.io/en/stable) and
[dppd](https://dppd.readthedocs.io/en/latest/)

It allows you to use code like this


```python
   import numpy as np
   from dppd import dppd
   import dppd_plotnine
   from plotnine.data import mtcars
   import plotnine as p9
   dp, X = dppd()

   plot = (
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
      .pd
    )
    plot.save("test.png")
    

```

![Example
image](https://github.com/TyberiusPrime/dppd_plotnine/raw/master/docs/_static/index.png)

Please see our full documentation at https://dppd_plotnine.readthedocs.io/en/latest/
for more details of the straight and enhanced plotnine mappings available.



