# API documentation of the gamspreprocessor package

`gamspreprocessor` is primarily ment to be used a command line tool, but it 
also provides a Python API, which is documented here. As great parts of the 
documentation is extracted automatically from docstrings, the API
documentation is only available in English.

If you'd like to use the API in your Python project, checking the code of
the `cli` module might be very helpful as an example of how to use
the API.

The package is organized organized in sub packages with dedicated purposes. 
The core API is simple, but this documentation also includes 

  - [project](project.md) - Initialize and manage a GAMS project.
  - [objectcsv](objectcsv.md) - Create and manage the csv files for additional metadata
  - [gams3](gams3.md) - Extract objects from GAMS 3 and store them as *object folders*
  - [projectsplitter](projectsplitter.md) - Transforms raw data, which was used as starting point for
    ingesting data to GAMS 3 using Cirilo into object directory which are required
    for ingesting to GAMS 5. If a project already is published on GAMS 3, you might
    preferece using the gams3 tool for object dir creation instead of projectsplitter. 
  - transformers - Provides tools for (mass) transformations of data (like XLST)