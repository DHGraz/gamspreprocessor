# preprocess

`preprocess` ist das zentrale Programm zum Erstellen und Verwalten GAMS Projekten.
Dabei wird für jedes Projekt ein eigenes Verzeichnis (["Projektordner"](object_dirs.md)) angelegt.


Es steht nach der Installation des Pakets `gamspreprocessor` zur Verfügung. 
Falls das Programm nicht gefunden wird, überprüfen Sie, ob das
korrekte virtuelle Environment aktiviert ist -- also das Environment in dem 
Sie `gamspreprocessor` installiert haben.

`preprocess` muss (fast) immer mit einem Unterbefehl aufgerufen werden, die
jeweils eigene Kommandozeilenoptionen und -argumente unterstützen. 

Sowohl `preprocess` selbst, als auch alle Unterbefehle unterstützen die
Option `--help`, die zur Ausgabe der Syntax und weiterer verfügbarer Optionen 
führt.


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
 

### Erzeugung und Update der Projektkonfiguration

   * [project](subcommands/project.md) - Initialisieren eines neuen Projekts

### Erzeugung und zur Pflege der CSV-Dateien

   * [csv](subcommands/csv.md) - Erstellung und Verwaltung von CSV-Dateien 
     (`object.csv` und `datastreams.csv`) in den einzelnen Objektordnern


### Erstellung der Objektverzeichnisse aus bestehenden Daten

   * [splitproject](subcommands/splitproject.md) - Zerlegt die Daten eines 
     alten GAMS 3 Projekts, wie sie unter `projekte` liegen, in Objektordner

   * [gams3export](subcommands/gams3export.md) 


### Systematisches Bearbeiten der Objektdaten      
   * [transform](subcommands/transform.md) - Ausführen einer Transformation 
     z.B. mit XSLT für einzelne Dateien
   * [multitransform](subcommands/multitransform.md) - Wie `transform`, aber 
     für viele Dateien

### Überprüfung der Objektverzeichnisse
   * [validate](subcommands/validate) - Validieren von Objektverzeichnissen  
  
