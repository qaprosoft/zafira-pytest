=============
pytest-zafira
=============

.. image:: https://img.shields.io/pypi/v/pytest-zafira.svg
    :target: https://pypi.org/project/pytest-zafira
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-zafira.svg
    :target: https://pypi.org/project/pytest-zafira
    :alt: Python versions

.. image:: https://travis-ci.org/KhDenys/pytest-zafira.svg?branch=master
    :target: https://travis-ci.org/Solvd.Inc/pytest-zafira
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/KhDenys/pytest-zafira?branch=master
    :target: https://ci.appveyor.com/project/Solvd.Inc/pytest-zafira/branch/master
    :alt: See Build Status on AppVeyor

A Zafira plugin for pytest
__________________________

Pytest plugin for integration with `Zafira`_.

----


Installation
------------

You can install "pytest-zafira" via `pip`_ from `PyPI`_::

    $ pip install pytest-zafira


Usage
-----

For usage follow the official documentation `Pytest`_.
Then add zafira_properties.ini file in the same place with conftest.py. File must look like::

 [config]
 base_url =
 service-url =
 zafira_enabled =
 access_token =
 job_name =
 suite_name =
 artifact_expires_in_default_time =
 aws_access_key =
 aws_secret_key =
 aws_screen_shot_bucket =
 s3_save_screenshots =


License
-------

Distributed under the terms of the `Apache Software License 2.0`_ license, "pytest-zafira" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Zafira`: https://github.com/qaprosoft/zafira
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`file an issue`: https://github.com/qaprosoft/pytest-zafira/issues
.. _`Pytest`: https://docs.pytest.org/en/latest/writing_plugins.html#requiring-loading-plugins-in-a-test-module-or-conftest-file
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
