# Changes from plotnine

## Call convention

The dppd_plotnine interface differes in two aspects from 
plotnine (and R's ggplot2) API:

Method-chaining replaces addition
``` python

   #plotnine

   p = p9.ggplot(df)
   p += p9.geom_point(p9.aes('x','y'), color='red')

   #dppd_plotnine
   dp(df).p9.geom_point(p9.aes('x','y'), color='red').pd

```



And optionally, aes mapping and kwargs are replaced by kwargs starting with and
without underscore:
``` python
   dp(df).p9.add_point('x', y='y', _color='red').pd
```


All geom_* functions can be called as add_* with the following changes to the calling
api:

   * all REQUIRED_AES can be passed by position. The order is x,y, then alphabetically
   * kwargs that name an aes are mapped (ie. as if they were passed to
     mapping=p9.aes(...)).
   * kwargs starting with a '_' are treated as unmapped (ie. _color= get's passed as
     color= kwarg to the geom)
   * data, position and stat are left alone.
   * data=None turns the geom into an annotation.


This pythonifies the interface a bit and get's rid of the p9.aes boilerplate,
while maintaining full expressiveness.

Note that this also allows you to use geom_hline(300) without having to type
y_intercept=...


## Ways to pass in data

 1. As an expression evaluated in the context of the DataFrame, using patsy, mapped:
 ``add_point(x='df_column * 5', ...)``. Note that column named 'x * 5' takes precedence
 over a column 'x' multiplied by 5.

 1. As a mapped list, the size of the DataFrame: ``add_point(x=['a','b','c], ...)``

 1. As an unmapped list, the size of the DataFrame: ``add_point(_color=['red','blue','red','blue'])``

 1. As a mapped scalar: ``add_point(x='"a"' ...)``, note the inner quoting!

 1. As a unmapped scalar: ``add_point(..., _color='red')``

 1. A mapping may refer to stat derived variables, add_bar(x='x', y='stat(count)',
 stat=p9.stat_count)

 1. If data=None is passed, the geom is treated as an annotation and a DataFrame is
 constructed from the values of the mappend and unmapped arguments: ``add_point(data=None,
 x=5, y=10, _color='red')``



## Other changes from plotnine

   * the default stat on geom_bar is stat_identity.
   * save is verbose=False by default and returns the plot object
   * save is aliased to render
   * add_scatter is an alias for add_point
   * there is a small set of convinence wrappers - see
     [`dppd_plotnine.plotnine_extensions`](api/dppd_plotnine.html)






