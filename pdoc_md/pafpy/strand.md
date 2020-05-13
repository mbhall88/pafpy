Module pafpy.strand
===================
A module containing objects relating to the strand field within a PAF file.

Classes
-------

`Strand(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enum listing the possible values in the strand field of a PAF file.
    
    ## Example
    ```py
    from pafpy import Strand
    
    strand = Strand("-")
    assert strand == Strand.Reverse
    assert str(strand) == "-"
    ```

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `Forward`
    :

    `Reverse`
    :

    `Unmapped`
    :