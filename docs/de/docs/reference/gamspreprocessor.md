# preprocess

`gamspreprocessor`  (oder kurz: `preprocess`) ist das zentrale Programm beim Erstellen von Objektverzeichnissen.
Dabei wird für jedes Projekt ein eigenes Verzeichnis (["Projektverzeichnis"](object_dirs.md)) angelegt.


Es steht nach der Installation des Pakets `gamspreprocessor` zur Verfügung. 
Falls das Programm nicht gefunden wird, überprüfen Sie, ob das
korrekte virtuelle Environment aktiviert ist -- also das Environment in dem 
Sie `gamspreprocessor` installiert haben.

`gamspreprocessor` muss (fast) immer mit einem Unterbefehl aufgerufen werden, die
jeweils eigene Kommandozeilenoptionen und -argumente unterstützen. 

Sowohl `gamspreprocessor` selbst, als auch alle Unterbefehle unterstützen die
Option `--help`, die zur Ausgabe der Syntax und weiterer verfügbarer Optionen 
führt.


`gamspreprocessor` selbst kennt einige wenige globale Optionen. 

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
  * `--version`: Gibt die Version von `gamspreprocessor` aus.
  * `--help`: Gibt Hilfe für `gamspreprocessor` aus.  

Mit `gamspreprocessor --help` können Sie sich diese Optionen ausgeben lassen.

## Unterbefehle

Das Programm `gamspreprocessor` kennt eine Reihen von Subcommands, die jeweils 
in einem eigenen Dokument beschrieben werden. Deshalb werden die 
einzelnen Unterbefehle hier nur kurz beschrieben und und auf das ausführlichere 
Dokument verlinkt. Sie können sich aber auch mit
`gamspreprocessor <subcommand> --help` die Hilfe zu den einzelnen Unterbefehlen
anzeigen lassen.
 

Folgende Subcommands stehen zur Verfügung:

   * [project](#der-unterbefehl-project) - Initialisieren eines neuen Projekts
   * [csv](#der-unterbefehl-csv) - Erstellung und Verwaltung von CSV-Dateien 
     (`object.csv` und `datastreams.csv`) in den einzelnen Objektordnern
<!--     
   * [validate](#validate) - Validieren von Objektverzeichnissen  
-->
   * [transform](#der-unterbefehl-transform) - Ausführen einer Transformation 
     z.B. mit XSLT
   * [multitransform](#der-unterbefehl-multitransform) - Wie `transform`, aber 
     für viele Dateien
   * [splitproject](#der-unterbefehl-splitproject) - Zerlegt die Daten eines 
     alten GAMS 3 Projekts, wie sie unter `projekte` liegen, in Objektordner



### Der Unterbefehl project

[`gamspreprocessor project`](gamspreprocessor/project.md) stellt weitere Unterbefehle
für die Erzeugung und Aktualisierung eines GAMS-Projekts bereit. Dies ist der 
empfohlende Weg ein neues Projekt anzulegen.

Details und weitere Möglichkeiten zu diesem Unterbefehl finden Sie 
[hier](gamspreprocessor/project.md) oder via `gamspreprocessor project --help`.

### Der Unterbefehl csv

[`gamspreprocessor csv`](gamspreprocessor/csv.md) stellt einige Unterbefehle bereit,
mit denen die CSV Dateien mit den Objekt-Metadaten erzeugt und verwaltet 
werden können.


Details und weitere Möglichkeiten zu diesem Unterbefehl finden 
Sie [hier](gamspreprocessor/csv.md) oder via `gamspreprocessor csv --help`.

<!--
## Der Unterbefehl validate

`gamspreprocessor validate`(gamspreprocess/validate.md) kann bzw. sollte verwendet
werden, um ein oder mehrere Objektverzeichnisse auf ihre Korrektheit zu überprüfen. 

Deails und weitere Möglichkeiten zu diesem Unterbefehl find Sie 
[hier](gamspreprocessor/validate.md) oder via `gamspreprocessor validate --help`.
-->

### Der Unterbefehl transform

[`gamspreprocessor transform`](gamspreprocessor/transform.md) führt Transformationen
von Daten aus. Aktuell gibt es nur die Möglichkeit XSLT-Transformationen 
auszuführen (via Saxon).

Details und weitere Möglichkeiten zu diesem Unterbefehl finden 
Sie [hier](gamspreprocessor/transform.md) oder via 
`gamspreprocessor transform --help`.

### Der Unterbefehl multitransform

[`gamspreprocessor multitransform`](gamspreprocessor/multitransform.md) 
funktioniert gleich wie `gamspreprocessor transform`,
führt die Transformation aber auf viele Objekte aus. Das ist beispielsweise
praktisch, um via XSLT auf einen Schlag für alle Objekte Metadaten aus 
dem TEI Header in das zwingend vorgegebene DC.xml zu überführen.

Details und weitere Möglichkeiten zu diesem Unterbefehl finden 
Sie [hier](gamspreprocessor/multitransform.md) oder via 
`gamspreprocessor multitransform --help`.

### Der Unterbefehl splitproject

[`gamspreprocessor splitproject`](gamspreprocessor/splitproject.md) ist ein 
Mittel, um ein Projekt, wie es 
typischerweise in GAMS 3 vor dem Ingest angelegt wurde in eine
Struktur zu überführen, aus der Bags für den Ingest in GAMS 5 s
erzeugt werden können. Es zerlegt also das Projekt in 
Objektverzeichnisse, kopiert referenzierte Ressourcen und benennt
diese ggf. um.

Details und weitere Möglichkeiten zu diesem Unterbefehl finden 
Sie [hier](gamspreprocessor/splitproject.md) oder via 
`gamspreprocessor splitproject --help`.
