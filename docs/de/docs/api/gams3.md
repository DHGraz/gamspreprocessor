# gamspreprocessor.gams3

This module exports digital objects from a GAMS3 instance to
*object dirs*. The most important function is
[`export_objects()`](#gamspreprocessor.gams3.export_objects),
a generator function which yields `Gams3Object` objects
containing data about the export status.

::: gamspreprocessor.gams3
    options:
        members:
            - export_objects
            - Gams3Object
            - ExportError
        show_submodules: false
        inherited_memebers: false
