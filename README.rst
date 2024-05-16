======
dipper
======


.. image:: https://img.shields.io/pypi/v/dipper.svg
        :target: https://pypi.python.org/pypi/dipper

.. image:: https://img.shields.io/travis/clint/dipper.svg
        :target: https://travis-ci.com/clint/dipper

.. image:: https://readthedocs.org/projects/dipper/badge/?version=latest
        :target: https://dipper.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/github/license/clint/dipper.svg
    :target: https://github.com/clint/dipper/blob/master/LICENSE.txt
    :alt: GitHub license

.. image:: https://badges.gitter.im/bird-house/birdhouse.svg
    :target: https://gitter.im/bird-house/birdhouse?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
    :alt: Join the chat at https://gitter.im/bird-house/birdhouse

dipper (the bird)
  *Dipper is a stout little bird that thrives in fast-flowing rivers.*

This namesake Web Processing Service produces data files and maps on flood warning level forecasts in Europe on a seasonal scale.

Warning levels are produced for sub-basins that has an average area of 250km2 and are presented with a weekly resolution.

The warning levels are determined from a historical simulations for the past 30 years and applied on a 31 week seasonal forecast at the start of each month.

The color, if any, shows the level of the first occuring warning whithin the forecast period.
Note that a higher warning level occuring in a specifig sub-basin can be obscured by a lower level occuring closer in time, use the functionality to choose levels to explore this.
Color intensity is lower the later the warning occurs in the forecast period. This means that a clear vibrant color is close in time and a faded color is distant in time up to the maximum of forecast week 30 which is then barely visible.

Documentation
-------------

Learn more about dipper in its official documentation at
https://dipper.readthedocs.io.

Submit bug reports, questions and feature requests at
https://github.com/clint/dipper/issues

Contributing
------------

You can find information about contributing in our `Developer Guide`_.

Please use bumpversion_ to release a new version.


License
-------

* Free software: Apache Software License 2.0
* Documentation: https://dipper.readthedocs.io.


Credits
-------

This package was created with Cookiecutter_ and the `bird-house/cookiecutter-birdhouse`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`bird-house/cookiecutter-birdhouse`: https://github.com/bird-house/cookiecutter-birdhouse
.. _`Developer Guide`: https://dipper.readthedocs.io/en/latest/dev_guide.html
.. _bumpversion: https://dipper.readthedocs.io/en/latest/dev_guide.html#bump-a-new-version
