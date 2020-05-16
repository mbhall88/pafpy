# pafpy

A lightweight library for working with [PAF][PAF] (Pairwise mApping Format) files.

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/mbhall88/pafpy/Python_package)](https://github.com/mbhall88/pafpy/actions)
[![codecov](https://codecov.io/gh/mbhall88/pafpy/branch/master/graph/badge.svg)](https://codecov.io/gh/mbhall88/pafpy)
[![PyPI](https://img.shields.io/pypi/v/pafpy)](https://pypi.org/project/pafpy/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pafpy)
![License](https://img.shields.io/github/license/mbhall88/pafpy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Documentation**: <https://pafpy.xyz>

[TOC]: #

# Table of Contents
- [Install](#install)
  - [PyPi](#pypi)
  - [Conda](#conda)
  - [Locally](#locally)
- [Usage](#usage)
- [Contributing](#contributing)


## Install

### PyPi

```sh
pip install pafpy
```

### Conda

```sh
conda install -c bioconda pafpy
```

### Locally

If you would like to install locally, the recommended way is using [poetry][poetry].

```sh
git clone https://github.com/mbhall88/pafpy.git
cd pafpy
make install
# to check the library is installed run
poetry run python -c "from pafpy import PafRecord;print(str(PafRecord()))"
# you should see a (unmapped) PAF record printed to the terminal
# you can also run the tests if you like
make test-code
```

## Usage

For full usage, please refer to the [documentation][docs]. If there is any functionality
you feel is missing or would make `pafpy` more user-friendly, please raise an issue
with a feature request.

In the below basic usage pattern, we collect the [BLAST identity][blast] of all primary
alignments in our PAF file into a list.

```py
from typing import List
from pafpy import PafFile

path = "path/to/sample.paf"

identities: List[float] = []
with PafFile(path) as paf:
    for record in paf:
        if record.is_primary():
            identity = record.blast_identity()
            identities.append(identity)
```

Another use case might be that we want to get the identifiers of all records aligned to
a specific contig, but only keep the alignments where more than 50% of the query (read)
is aligned.

```py
from typing import List
from pafpy import PafFile

path = "path/to/sample.paf"

contig = "chr1"
min_covg = 0.5
identifiers: List[str] = []
with PafFile(path) as paf:
    for record in paf:
        if record.tname == contig and record.query_coverage > min_covg:
            identifiers.append(record.qname)
```

## Contributing

If you would like to contribute to `pafpy`, checkout [`CONTRIBUTING.md`][contribute].

[poetry]: https://python-poetry.org/
[PAF]: https://github.com/lh3/miniasm/blob/master/PAF.md
[docs]: https://pafpy.xyz/
[blast]: https://lh3.github.io/2018/11/25/on-the-definition-of-sequence-identity#blast-identity
[contribute]: https://github.com/mbhall88/pafpy/blob/master/CONTRIBUTING.md

