# preprocess

`preprocess` ist das zentrale Programm beim Erstellen von Objektverzeichnissen.
Es steht nach der Installation des Pakets `gamspreprocessor` zur Verfügung. 
Falls das Programm nicht gefunden wird, überprüfen Sie, ob das
korrekte virtuelle Environment aktiviert ist -- also das Environment in dem 
Sie `gamspreprocessor` installiert haben.

`preprocess` muss (fast) immer mit einem Unterbefehl aufgerufen werden, die
jeweils eigene Kommandozeilenoptionen und -argumente unterstützen. 
`preprocess` selbst kennt einige wenige globale Optionen. 

## Globale Optionen

Globale Optionen sind **vor** dem jewiligen Unterbefehl anzugeben und stehen global, also unabhängig von einem spezifischen Unterbefehl zur Verfügung. Diese globalen Optionen sind:

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
einzelnen Unterbefehle hier nur kurz beschrieben und und auf das ausführlichere 
Dokument verlinkt. Sie können sich aber auch mit
`preprocess <subcommand> --help` die Hilfe zu den einzelnen Unterbefehlen
anzeigen lassen.
 

Folgende Subcommands stehen zur Verfügung:

   * [project](#der-unterbefehl-project) - Initialisieren eines neuen Projekts
   * [csv](#der-unterbefehl-csv) - Erstellung und Verwaltung von CSV-Dateien 
     (`object.csv` und `datastreams.csv`) in den einzelnen Objektordnern
   * [validate](#validate) - Validieren von Objektverzeichnissen  
   * [transform](#der-unterbefehl-transform) - Ausführen einer Transformation 
     z.B. mit XSLT
   * [multitransform](#der-unterbefehl-multitransform) - Wie `transform`, aber 
     für viele Dateien
   * [splitproject](#der-unterbefehl-splitproject) - Zerlegt die Daten eines 
     alten GAMS 3 Projekts, wie sie unter `projekte` liegen, in Objektordner



### Der Unterbefehl project

[`preprocess project`](preprocess/project.md) stellt weitere Unterbefehle für die Erzeugung und Aktualisierung
eines GAMS-Projekts bereit. Dies ist der empfohlende Weg ein neues Projekt anzulegen.

Details und weitere Möglichkeiten zu diesem Unterbefehl finden Sie 
[hier](preprocess/project.md) oder via `preprocess project --help`.

### Der Unterbefehl csv

[`preprocess csv`](preprocess/csv.md) stellt einige Unterbefehle bereit, mit denen die CSV Dateien
mit den Objekt-Metadaten erzeugt und verwaltet werden könne.


Details und weitere Möglichkeiten zu diesem Unterbefehl finden 
Sie [hier](preprocess/csv.md) oder via `preprocess csv --help`.

## Der Unterbefehl validate

`preprocess validate`(preprocess/validate.md) kann bzw. sollte verwendet werden, um ein oder
mehrere Objektverzeichnisse auf ihre Korrektheit zu überprüfen. 

Deails und weitere Möglichkeiten zu diesem Unterbefehl find Sie [hier](preprocess/validate.md) 
oder via `preprocess validate --help`.

### Der Unterbefehl transform

[`preprocess transform`](preprocess/transform.md) führt Transformationen von Daten aus. Aktuell
gibt es nur die Möglichkeit XSLT-Transformationen auszuhühren (via Saxon).

Details und weitere Möglichkeiten zu diesem Unterbefehl finden 
Sie [hier](preprocess/transform.md) oder via `preprocess transform --help`.

### Der Unterbefehl multitransform

[`preprocess multitransform`](preprocess/multitransform.md) funktioniert gleich wie `preprocess transform`,
führt die Transformation aber auf viele Objekte aus. Das ist beispielsweise
praktisch, um via XSLT auf einen Schlag für alle Objekte Metadaten aus 
dem TEI Header in das zwingend vorgegebene DC.xml zu überführen.

Details und weitere Möglichkeiten zu diesem Unterbefehl finden 
Sie [hier](preprocess/multitransform.md) oder via `preprocess multitransform --help`.

### Der Unterbefehl splitproject

[`preprocess splitproject`](preprocess/splitproject.md) ist ein Mittel, um ein Projekt, wie es 
typischerweise in GAMS 3 vor dem Ingest angelegt wurde in eine
Struktur zu überführen, aus der Bags für den Ingest in GAMS 5 s
erzeugt werden können. Es zerlegt also das Projekt in 
Objektverzeichnisse, kopiert referenzierte Ressourcen und benennt
diese ggf. um.

Details und weitere Möglichkeiten zu diesem Unterbefehl finden 
Sie [hier](preprocess/splitproject.md) oder via 
`preprocess splitproject --help`.
