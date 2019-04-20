The test directory may contain three subdirectories:

* `scripts` - locally-defined tests
* `inputs` - Data files and input parameters for applying tests
* `expected` - Expected results of tests

The `inputs` and `expected` directories may contain large files and may be better handled
via [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) and
[DataLad](http://docs.datalad.org) than by directly including them in the repository.
