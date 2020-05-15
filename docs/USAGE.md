# Usage

If there is any functionality you feel is missing, or would make `pafpy` more
user-friendly, please [raise an issue][issue] with a feature request.

## Basic

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

## Advanced

### Manual open/close

Sometimes a `with` context manager is not appropriate and you would like to manually
open the file and pass it around. This can be achieved using the
`pafpy.paffile.PafFile.open` and `pafpy.paffile.PafFile.close` methods. As an example,
let's say we define a function that takes a `pafpy.paffile.PafFile` and counts the number of records in it.

```py
from pafpy import PafFile

def count_records(paf: PafFile) -> int:
    """Counts the number of alignments in a PAF file."""
    return sum(1 for _ in paf)
    
path = "path/to/sample.paf"

paf = PafFile(path).open()
num_records = count_records(paf)
# it's good practise to close the file yourself rather than rely on the garbage collector
paf.close()
assert paf.closed
```

Admittedly, this is a contrived example and we could have still used the context manager, but you get the point 😉.

### Fetch individual records

`for` loops aren't the only way of retrieving records in a file. You can also ask for records manually.

```py
from pafpy import PafFile

path = "path/to/sample.paf"

with PafFile(path) as paf:
    record = next(paf)
# do something with our lonely record
```

### Working with strands

There is a special enum for representing the strand field - `pafpy.strand.Strand`. This has a couple of advantages over just using a `str`, but the main one if readability. Let's count the number of records that mapped to the reverse strand.

```py
from pafpy import PafFile, Strand

path = "path/to/sample.paf"

num_reverse = 0
with PafFile(path) as paf:
    for record in paf:
        if record.strand is Strand.Reverse:
            num_reverse += 1
```

You can convert strands to and from `str` quite easily.

```py
from pafpy import Strand

assert Strand("+") is Strand.Forward
assert str(Strand.Reverse) == "-"
assert str(Strand.Unmapped) == "*"
```

### PAF records

The object you will likely spend most time with is `pafpy.pafrecord.PafRecord`. Refer to
the API docs for documentation on all the functions and member variables this class contains.

Let's look at a few use cases though. Construction of `PafRecord`s is quite flexible as we wanted to make it very easy to write unit tests and construct arbitrary records without having to construct and entire PAF file just to do so.  
There are two ways to construct a `PafRecord`:

1. The default constructor, where you specify each member variable manually.
2. Using the `pafpy.pafrecord.PafRecord.from_str` factory constructor method.

```py
from pafpy import PafRecord, Strand, Tag

# default constructor
record1 = PafRecord(
        qname="query_name",
        qlen=1239,
        qstart=65,
        qend=1239,
        strand=Strand.Forward,
        tname="target_name",
        tlen=4378340,
        tstart=2555250,
        tend=2556472,
        mlen=1139,
        blen=1228,
        mapq=60,
        tags={"NM": Tag.from_str("NM:i:8")},
)

# from_str factory constructor
line = "query_name\t1239\t65\t1239\t+\ttarget_name\t4378340\t2555250\t2556472\t1139\t1228\t60\tNM:i:8"
record2 = PafRecord.from_str(line)

assert record1 == record2
```

### SAM-like optional fields/tags

Each additional column after the 12th column in a PAF file is a [SAM-like tag][tag]. The `pafpy.tag.Tag` class tries to make working with tags much easier. You can extract these from a `PafRecord` using `pafpy.pafrecord.PafRecord.get_tag` or you may like to construct one yourself.  
Let's look at some of these options.

```py
from pafpy import PafRecord, Tag

line = "query_name\t1239\t65\t1239\t+\ttarget_name\t4378340\t2555250\t2556472\t1139\t1228\t60\tNM:i:8"
record = PafRecord.from_str(line)

tag = record.get_tag("NM")
assert tag.tag == "NM"
assert tag.type == "i"
assert tag.value == 8

# we can construct tags from scratch with a str
tag = Tag.from_str("tp:A:P"
assert tag.value == "P"

# or with the default constructor
tag = Tag(tag="de", type="f", value=0.2)
```

One thing to notice is that the `value` is in the correct type as specified in the [tag specs][tag]. However, if you define a `Tag` with the default constructor, you can bypass this. The `pafpy.tag.Tag.from_str` method validates the tag string to ensure it strictly matches the specifications. As such, we recommend using this method when constructing tags. But, there may be cases where you don't want to adhere to this convention, and in those cases, use the default constructor.

```py
from pafpy import Tag, InvalidTagFormat

# type 'i' signifies an integer
tag = Tag(tag="NM", type="i", value="foo")
assert tag.value == "foo"

# if we try and do this with from_str we get an error
tag = None
err_msg = ""
try:
    tag = Tag.from_str("NM:i:foo")
except InvalidTagFormat as err:
    err_msg = str(err)
assert err_msg == "NM:i:foo is not in the correct tag format."
```

[blast]: https://lh3.github.io/2018/11/25/on-the-definition-of-sequence-identity#blast-identity
[issue]: https://github.com/mbhall88/pafpy/issues
[tag]: https://samtools.github.io/hts-specs/SAMtags.pdf

