"""A light-weight library for working with [PAF][PAF] (Pairwise mApping Format) files.

<!--[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/mbhall88/pafpy/Python_package)](https://github.com/mbhall88/pafpy/actions)-->
<!--[![codecov](https://codecov.io/gh/mbhall88/pafpy/branch/master/graph/badge.svg)](https://codecov.io/gh/mbhall88/pafpy)-->

![License](https://img.shields.io/github/license/mbhall88/pafpy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# Install

### PyPi

```shell
pip install pafpy
```

### Conda

```shell
conda install -c bioconda pafpy
```

### Locally

If you would like to install locally, the recommended way is using [poetry][poetry].

```shell
git clone https://github.com/mbhall88/pafpy.git
cd pafpy
make install
# to check the library is installed run
poetry run python -c "from pafpy import PafRecord;print(str(PafRecord()))"
# you should see a (unmapped) PAF record printed to the terminal
# you can also run the tests if you like
make test-code
```

.. include:: ../docs/USAGE.md

[poetry]: https://python-poetry.org/
[PAF]: https://github.com/lh3/miniasm/blob/master/PAF.md
[docs]: #TODO
[blast]: https://lh3.github.io/2018/11/25/on-the-definition-of-sequence-identity#blast-identity
[contribute]: https://github.com/mbhall88/pafpy/blob/master/CONTRIBUTING.md

.. include:: ../CONTRIBUTING.md
"""
from pafpy.paffile import PafFile  # noqa: F401
from pafpy.pafrecord import PafRecord, MalformattedRecord, AlignmentType   # noqa: F401
from pafpy.strand import Strand  # noqa: F401
from pafpy.tag import Tag, TagType, TagTypes, InvalidTagFormat, UnknownTagTypeChar  # noqa: F401
