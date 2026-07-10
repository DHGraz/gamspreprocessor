# gamspreprocessor.projectsplitter

Splits up a directory structure typically used for GAMS 3 ingest into 
*object directories* expected by the SIP packager of GAMS 5.

If an object already exists in a GAMS3 repository, using the [gamspreprocessor.gams3](gams3.md) exporter might be easier to use. 

The important functions API wise are:

   - [split_project_files()](#gamspreprocessor.projectsplitter.split_project_files) - Split one or more source files into object directories.
   - [list_unhandled()](#gamspreprocessor.projectsplitter.list_unhandled_files) - Return 
        files that are still unhandled in the given object directory tree.

::: gamspreprocessor.projectsplitter
    options:
        members:
            - list_unhandled_files
            - split_project_files
            - BookKeeper
            - ProjectSplitter
        show_submodules: false
        inherited_members: false