# Der Unterbefehl transform

Dieser Unterbefehl transformiert den Inhalt einer Datei und schreibt das Ergebnis in eine neue Datei.

Um mehrere Dateien auf einen Schlag umzuwandeln, verwenden Sie diesen Befehl mehrfach z.B. in einem 
Shellscript oder verwenden statt dessen den Unterbefehl [multitransform](./multitransform.md).

## Verwendung 

```
gamspreprocessor transform [OPTIONS] COMMAND [ARGS]...
```

## Unterbefehle

* `xslt` Wendet eine XSL Transformation an
* `saxon-version` Zeigt die Version des Saxon Prozessors


### xslt

`gamspreprocessor transform xslt -x <XSLT-DATEI> <EINGABEDATEI> <AUSGABEDATEI>` 
wendet die XSL Transformation `XSLT-DATEI` auf die Ausgangsdatei `EINGABEDATEI` an und schreibt das Ergebnis in die Datei
`AUSGABEDATEI`.

```
gamspreprocessor transform xslt [OPTIONS] XML_FILE OUTPUT_FILE
```

#### Optionen:
    
##### `--xslt-file <PFAD>`, `-x <PFAD>` 

Legt den Pfad zur anzuwendenden XSLT Datei fest. Die Option MUSS verwendet werden.

##### `--help`

Zeigt den Hilfetext für diesen Unterbefehl an.


### xslt-processor

Über diesen Unterbefehl lässt sich die genaue Version des verwendeten XSLT Prozessors herausfinden.

```
gamspreprocessor transform xslt-processor
```

zeigt die Version des installierten XSLT Prozessors

#### Optionen 

##### `--help`

Zeigt den Hilfetext für diesen Unterbefehl an.