# preprocess

`preprocess` ist das zentrale Programm beim Erstellen von Objektverzeichnissen.
Es steht nach der Installation des Pakets `gamspreprocessor` zur Verfügung. 
Falls das Programm nicht gefunden wird, überprüfen Sie, ob das
korrekte virtuelle Environment aktiviert ist -- also das Environment in dem 
Sie `gamspreprocessor` installiert haben.

`preprocess` muss (fast) immer mit einem Unterbefehl aufgerufen werden, die
jeweils eigene Kommandozeilenoptionen und -argumente unterstützen. 
`preprocess` selbst kennt einige wenige globake Optionen. Diese sind:

  * `--verbose` bzw. `-v`: Führt zu zusätzlichen Zeilen in der Ausgabe. Darf nicht
    zusammen mit `--qiet` verwendet werden. `--verbose` kann bei hilfreich bei
    der Fehlersuche sein.
  * `--quiet` bzw. `-q`: Unterdrückt die Auusgabe auf der Kommandozeile. Kann
    nicht zusammen mit `--verbose` verwendet werden.   
  * `--logfile`: Name (oder Pfad) einer Datei, in die geloggt werden soll.
    Ist diese Option nicht gesetzt, wird nur auf die Kommandozeile geloggt.
  * `--filelog-level`: Legt die Gesprächigkeit für die Logdatei fest.
    Erlaubte Werte sind: `DEBUG`, `INFO`, `WARNING`, `ERROR` oder 
    `CRITICAL`.
  * `--version`: Gibt die Version von `preprocess` aus.
  * `--help`: Gibt Hilfe für `preprocess` aus.  

Mit `preprocess --help` können Sie sich diese Optionen ausgeben lassen.

## Unterbefehle

Das Programm `preprocess` kennt eine Reihen von Subcommands, die jeweils 
in einem eigenen Dokument beschrieben werden. Deshalb werden die 
Unterbefehle hier nur sehr kurz beschrieben und und auf die ausführlicheren 
Dokumente verlinkt. Sie können sich aber auch mit
`preprocess <subcommand> --help` die Hilfe zu den einzelnen Unterbefehlen
anzeigen lassen.
 

Folgende Subcommands stehen zur Verfügung:

   * [project](###preprocess-project) - Initialisieren eines neuen Projekts
   * [csv](###preprocess-csv) - Erstellung und Verwaltung von CSV-Dateien 
     (`object.csv` und `datastreams.csv`) in den einzelnen Objektordnern
   * [transform](preprocess-transform) - Ausführen einer Transformation 
     z.B. mit XSLT
   * [multitransform](preprocess-multitransform) - Wie `transform`, aber 
     für viele Dateien.
   * [splitproject](preprocess-splitproject) - Zerlegt die Daten eines 
     alten GAMS-Projekts in Objektordner


### preprocess project

`preprocess project` stellt Unterbefehle für die Erzeugung und Aktualisierung
eines GAMS-Projekts bereit.

```
preprocess project init <pfad>
```

legt ein Gerüst für ein neues Projekt im Verzeichnis `<pfad>` an. Danach
muss noch die Konfiguration in der Datei `<pfad>/project.toml` an das Projekt 
angepasst werden.

Details und weitere Möglichkeiten zu diesem Unterbefehl finden Sie in 
Sie [hier](./commands/project.md) oder via `preprocess project --help`.

### preprocess csv

`preprocess csv` stellt einige Unterbefehle bereit, mit denen die CSV Dateien
mit den Objekt-Metadaten erzeugt und verwaltet werden könne.


Details und weitere Möglichkeiten zu diesem Unterbefehl finden Sie in 
Sie [hier](./commands/csv.md) oder via `preprocess csv --help`.


### preprocess transform

`preprocess transform` führt Transformationen von Daten aus. Aktuell
gibt es nur die Möglichkeit XSLT-Transformationen auszuhühren (via Saxon).

Details und weitere Möglichkeiten zu diesem Unterbefehl finden Sie in 
Sie [hier](./commands/transform.md) oder via `preprocess transform --help`.

### preprocess multitransform

`preprocess multitransform` funktioniert gleich wie `preprocess transform`,
führt die Transformation aber auf viele Objekte aus. Das ist beispielsweise
praktisch, um via XSLT auf einen Schlag für alle Objekte Metadaten aus 
dem TEI Header in das zwingend vorgegebene DC.xml zu überführen.

Details und weitere Möglichkeiten zu diesem Unterbefehl finden Sie in 
Sie [hier](./commands/multitransform.md) oder via `preprocess multitransform --help`.

### preprocess splitproject

`preprocess splitproject` ist ein Mittel, um ein Projekt, wie es 
typischerweise in GAMS 3 vor dem Ingest angelegt wurde in eine
Struktur zu überführen, aus der Bags für den Ingest in GAMS 5 
erzeugt werden können. Es zerlegt also das Projekt in 
Objektverzeichnisse, kopiert referenzierte Ressourcen und benennt
diese ggf. um.

Details und weitere Möglichkeiten zu diesem Unterbefehl finden Sie in 
Sie [hier](./commands/splitproject.md) oder via 
`preprocess splitproject --help`.
