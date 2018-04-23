R Stats
=======

Installing dependencies
-----------------------

To install **R** dependencies (command line):

    Rscript install.R

Energy/Power Database
---------------------

You may use these scripts with any database created by the Python
scripts outside this directory; however, for the Docker paper, we used
the database linked here:

> energy.sqlite: [10.5281/zenodo.1227250](https://doi.org/10.5281/zenodo.1227250)
>
> SHA256 checksum: `3c0af704aae41e48423abf481df7cf682363c69702f7e034ddafd471d74c186f`


Running
-------

All of the following scripts use `common.R` which assumes
`energy.sqlite` is in the current working directory.


`ttesting.R` does many assorted stats.

`power-plots.R` produces power-over-time hex plots using ggplot2.


License
=======

Copyright (C) 2016–2018 Eddie Antonio Santos, Carson McLean, Christopher
Solinas. Licensed under the terms of the
[CRAPL](http://matt.might.net/articles/crapl/) license. We're sorry.
