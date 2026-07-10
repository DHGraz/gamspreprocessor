# gamspreprocessor.objectcsv

The `csv` submodule provides function to create and manage the csv files containing addition metadata
for an object (`object.csv`) and datastreams (`datastreams.csv`).

The important functions API wise are:

  - [create_csv_files()](#gamspreprocessor.objectcsv.create_csv_files) - Generate 
        object and datastream CSV files for a project tree
  - [collect_csv_files](#gamspreprocessor.objectcsv.collect_csv_data) - Collect 
        per-object CSV files into a combined XLSX or CSV export
  - [update_csv_files](#gamspreprocessor.objectcsv.update_csv_files) - Update 
        per-object CSV files from a combined XLSX or CSV export


::: gamspreprocessor.objectcsv
