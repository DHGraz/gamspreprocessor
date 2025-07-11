# transform

Hilfsfunktionen um GAMS-Dateien umzuwandeln. Diese Befehle können hilfreich sein, um GAMS-Dateien in andere Formate zu übertragen.

## Verwendung 

```
preprocess transform [OPTIONS] COMMAND [ARGS]...
```
* Optionen:
    * --help
        Zeigt Hilfe für diesen Befehl an

## Unterbefehle

* `preprocess transform saxon-version` Zeigt die Version des Saxon Prozessors
* `preprocess transform xslt` Teilt Projektdateien in Objektordner auf

### preprocess transform saxon-version

`preprocess transform saxon-version` Zeigt die Version des Saxon Prozessors.

```
preprocess transform saxon-version [OPTIONS]
```
* Zeigt die Version des Saxon Prozessors
* Optionen: 
    * --help
        Zeigt Hilfe für diesen Befehl an

### preprocess transform xslt

`preprocess transform xslt` Wendet eine xslt auf eine einzelne xml Datei an

```
preprocess transform xslt [OPTIONS] XML_FILE OUTPUT_FILE
```

* Optionen:
    * -x, --xslt-file PATH 
        ###COMMENT: hier gab es keinen Text, bei multitransform steht, dieser Pfad müsse immer angegbene werden. ###
    * --help
        Zeigt Hilfe für diesen Befehl an