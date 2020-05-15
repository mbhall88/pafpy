Module pafpy.pafrecord
======================
This module contains objects for working with single alignment records within a PAF
file.

The main class of interest here is `PafRecord`. It provides a set of member
variables relating to each field within the record, as well as some convenience methods
for common tasks.

To use `PafRecord` within your code, import it like so

```py
from pafpy import PafRecord
```

Classes
-------

`AlignmentType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enum for storing mappings between the value in the `tp` tag and the type of
    alignment this value indicates.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `Inversion`
    :

    `Primary`
    :

    `Secondary`
    :

    `Unknown`
    :

`MalformattedRecord(...)`
:   An exception indicating that a `PafRecord` is not in the expected format.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`PafRecord(qname: str = '*', qlen: int = 0, qstart: int = 0, qend: int = 0, strand: pafpy.strand.Strand = *, tname: str = '*', tlen: int = 0, tstart: int = 0, tend: int = 0, mlen: int = 0, blen: int = 0, mapq: int = 255, tags: Union[Dict[str, pafpy.tag.Tag], NoneType] = None)`
:   A single entry (row) in a [PAF][paf] file.
    
    There are two ways to construct a `PafRecord`:
    
    1. The default constructor, where you specify each member variable manually.
    2. Using the `PafRecord.from_str` factory constructor method.
    
    ## Example
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
    line = "query_name  1239    65      1239    +       target_name     4378340 2555250 2556472 1139    1228    60      NM:i:8"
    record2 = PafRecord.from_str(line)
    
    assert record1 == record2
    ```
    
    [paf]: https://github.com/lh3/miniasm/blob/master/PAF.md

    ### Ancestors (in MRO)

    * builtins.tuple

    ### Static methods

    `from_str(line: str) -> pafpy.pafrecord.PafRecord`
    :   Construct a `PafRecord` from a string.
        
        > *Note: If there are duplicate SAM-like tags, only the last one will be
        retained.*
        
        ## Example
        ```py
        from pafpy import PafRecord
        
        line = "query_name      123     65      123     +       tname   43783   25552   25564   1139    1228    60"
        record = PafRecord.from_str(line)
        
        assert record.qname == "query_name"
        assert record.mapq == 60
        ```
        
        ## Errors
        - If there are less than the expected number of fields (12), this function will
        raise a `MalformattedRecord` exception.
        - If there is an invalid tag, an `pafpy.tag.InvalidTagFormat` exception will
        be raised.

    ### Instance variables

    `blen`
    :   Alignment block length. Number of bases, including gaps, in the mapping.

    `mapq`
    :   Mapping quality (0-255; 255 for missing).

    `mlen`
    :   Number of matching bases in the mapping.

    `qend`
    :   Query end (0-based; BED-like; open).

    `qlen`
    :   Query sequence length.

    `qname`
    :   Query sequence name.

    `qstart`
    :   Query start (0-based; BED-like; closed).

    `query_aligned_length`
    :   Length of the aligned query sequence.
        
        This is equal to the absolute value of `PafRecord.qend` - `PafRecord.qstart`.

    `query_coverage`
    :   Proportion of the query sequence involved in the alignment.
        
        This is equal to `PafRecord.query_aligned_length` - `PafRecord.qlen`
        
        ## Example
        ```py
        from pafpy import PafRecord
        
        record = PafRecord(qlen=10, qstart=5, qend=9)
        assert record.query_coverage == 0.4
        ```

    `relative_length`
    :   Relative (aligned) length of the query sequence to the target.
        
        This is equal to `PafRecord.query_aligned_length` -
        `PafRecord.target_aligned_length`.
        
        ## Example
        ```py
        from pafpy import PafRecord
        
        record = PafRecord(qlen=50, qstart=10, qend=20, tlen=100, tstart=50, tend=90)
        assert record.relative_length == 0.25
        ```

    `strand`
    :   `pafpy.strand.Strand.Forward` if query/target on the same strand; 
        `pafpy.strand.Strand.Reverse` if opposite; 
        `pafpy.strand.Strand.Unmapped` if unmapped.

    `tags`
    :   [SAM-like optional fields (tags)](https://samtools.github.io/hts-specs/SAMtags.pdf). 
        It is recommended to use `PafRecord.get_tag` to retrieve individual tags.

    `target_aligned_length`
    :   Length of the aligned target sequence.
        
        This is equal to the absolute value of `PafRecord.tend` - `PafRecord.tstart`.

    `target_coverage`
    :   Proportion of the target sequence involved in the alignment.
        
        This is equal to `PafRecord.target_aligned_length` - `PafRecord.tlen`
        
        ## Example
        ```py
        from pafpy import PafRecord
        
        record = PafRecord(tlen=10, tstart=5, tend=9)
        assert record.target_coverage == 0.4
        ```

    `tend`
    :   Target end on original strand (0-based).

    `tlen`
    :   Target sequence length.

    `tname`
    :   Target sequence name.

    `tstart`
    :   Target start on original strand (0-based).

    ### Methods

    `blast_identity(self) -> float`
    :   Calculates the [BLAST identity][blast] for the record.
        
        BLAST identity is defined as the number of matching bases (`PafRecord.mlen`)
        over the number of alignment columns (`PafRecord.blen`).
        
         > *Note: If your PAF file was generated from minimap2, it is strongly advised
        that you ensure either the `-c` or `--cs` options were used when generating the
        alignment, otherwise the BLAST identity will be very inaccurate. See the
        [minimap2 FAQ][faq] for more information.*
        
        ## Example
        ```py
        from pafpy import PafRecord
        
        record = PafRecord(
            mlen=43,  # number of matches
            blen=50,  # number of alignment columns
        )
        assert record.blast_identity() == 0.86
        ```
        [blast]: https://lh3.github.io/2018/11/25/on-the-definition-of-sequence-identity#blast-identity
        [faq]: https://github.com/lh3/minimap2/blob/master/FAQ.md#1-alignment-different-with-option--a-or--c

    `get_tag(self, tag: str, default: Union[pafpy.tag.Tag, NoneType] = None) -> Union[pafpy.tag.Tag, NoneType]`
    :   Retreive a tag from the record if it is present. Otherwise, return `default`.
        
        If `default` is not specified, `None` will be used as the default.
        
        ## Example
        ```py
        from pafpy import PafRecord, Tag
        
        # tag is present
        expected = Tag.from_str("de:f:0.1")
        tags = {"de": expected}
        record = PafRecord(tags=tags)
        tag = "de"
        
        actual = record.get_tag(tag)
        
        assert actual == expected
        
        # tag is not present, returns default
        tag = "NM"
        default = Tag.from_str("NM:i:0")
        
        actual = record.get_tag(tag, default=default)
        
        assert actual == default
        ```

    `is_inversion(self) -> bool`
    :   Is the alignment an inversion?
        
        This is determined from the [`tp` tag][mm2-tags]. For more information about
        inversions (from minimap2) refer to the [minimap2 alignment options][aln-opts].
        
        ## Example
        ```py
        from pafpy import PafRecord, Strand, Tag
        
        tag = Tag.from_str("tp:A:I")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})
        assert record.is_inversion()
        ```
        
        ## Errors
        If the value in the `tp` tag is unknown, a `ValueError` exception will be
        raised.
        
        [mm2-tags]: https://lh3.github.io/minimap2/minimap2.html#10
        [aln-opts]: https://lh3.github.io/minimap2/minimap2.html#6

    `is_primary(self) -> bool`
    :   Is the record a primary alignment?
        
        This is determined from the [`tp` tag][mm2-tags].
        
        > *Note: Supplementary alignments will also return `True`.*
        
        ## Example
        ```py
        from pafpy import PafRecord, Strand, Tag
        
        tag = Tag.from_str("tp:A:P")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})
        assert record.is_primary()
        ```
        
        ## Errors
        If the value in the `tp` tag is unknown, a `ValueError` exception will be
        raised.
        
        [mm2-tags]: https://lh3.github.io/minimap2/minimap2.html#10

    `is_secondary(self) -> bool`
    :   Is the record a secondary alignment?
        
        This is determined from the [`tp` tag][mm2-tags].
        
        > *Note: Supplementary alignments will return `False` as they are considered
        primary.*
        
        ## Example
        ```py
        from pafpy import PafRecord, Strand, Tag
        
        tag = Tag.from_str("tp:A:S")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})
        assert record.is_secondary()
        ```
        
        ## Errors
        If the value in the `tp` tag is unknown, a `ValueError` exception will be
        raised.
        
        [mm2-tags]: https://lh3.github.io/minimap2/minimap2.html#10

    `is_unmapped(self) -> bool`
    :   Is the record unmapped?
        
        A record is considered unmapped if the strand is '*'
        (`pafpy.strand.Strand.Unmapped`) - as per the minimap2
        [`--paf-no-hit`][io-opts] parameter behaviour.
        
        ## Example
        ```py
        from pafpy import PafRecord, Strand
        
        record = PafRecord(strand=Strand("*"))
        assert record.is_unmapped()
        ```
        
        [io-opts]: https://lh3.github.io/minimap2/minimap2.html#7