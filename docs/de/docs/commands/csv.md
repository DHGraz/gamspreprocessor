# Der Unterbefehl csv

Hilfsfunktionen mit denen die CSV Dateien mit den Objekt-Metadaten erzeugt und verwaltet werden.

## Verwendungszweck

Der Gams-Packager, der die Bagit-Pakete für den Ingest erzeugt, benötigt einige
Metadaten, die das Paket und die darin enthaltenen Dateien beschreibt. Da diese
Daten nicht vollständig aus den Dateien selbst abgeleitet werden können, erwartet
der Packager in jedem Objektverzeichnis (jedes Objekt muss in einem eigenen Verzeichnis
liegen) zwei CSV-Dateien:

   * object.csv
   * datastreams.csv
  
Diese beiden Dateien landen nicht im Bag, werden aber für die Erzeugung der Bag-Metadaten
gebraucht. Da die händische Erzeugung und Pflege dieser CSV-Dateien sehr mühsam ist,
stellt der `csv` Unterbefehl von `preprocess` nützliche Funktionen dafür bereit.

Ein prototypischer Ablauf sieht so aus:

  1. Erstellung der Objektordner (z.B. via `updatecsv split`). Wichtig dabei ist,
     dass in jedem Objektordner eine Datei `DC.xml` vorhanden ist. Diese kann
     z.B. via XSLT aus einem TEI erzeugt werden (siehe 
     `preprocess multitransform`).
  1. Ist diese Voraussetzung erfüllt, und zusätzlich die Projekt-Konfigurationsdatei
     `project.toml` erzeugt (siehe `preprocess init`), können mit dem Befehl
     `preprocess csv create OBJECT_ROOT` für alle Objektordner unterhalb von `OBJECT_ROOT`
     diese beiden CSV Dateien erzeugt werden.
  1. Gibt es mehrere oder sogar viele Projektordner, wäre die separate Bearbeitung der 
     einzelnen CSV-Dateien sehr mühsam. Deshalb wird empfohlen, mit dem Befehl
     `preprocess csv collect` alle CSV-Daten aus den einzelnen  Objektordnern
     einzusammeln und zusammen in eine Excel-Datei `all_objects.csv` zu speichern.
     Diese Datei kann dann sehr effizient bearbeitet werden, indem beispielsweise
     die Einträge nach bestimmten Spalten sortiert werden und/oder fehlende Werte
     in viele Zeilen gleichzeitig hineinkopiert werden. 
  1. Ist die Bearbeitung von `all_objects.csv` abgeschlossen, werden die dort
     vorgenommenen Änderungen mit dem Befehl `preprocess csv update` wieder in
     die einzelnen CSV-Datei zurückgespielt. `all_objects.csv` sollte danach
     aus Konsistenzgründen gelöscht werden, da die Datei jederzeit neu
     via `preprocess csv collect` erzeugt werden kann.



## Verwendung 

```
preprocess csv [OPTIONS] COMMAND [ARGS]
```

## Unterbefehle

* `create` Generiert CSV Dateien mit Metadaten für Objektverzeichnisse
* `collect` Sammelt Daten von allen CSV Dateien in allen Objektordnern
* `update` Aktualisiert Objekt- und Datenstrom CSV Dateien anhand der gesammelten CSV Dateien
* `csv2xslx` Konvertiert CSV-Dateien in XLSX-Dateien (wird normalerweise nicht benötigt)
* `xlsx2csv` Konvertiert XLSX-Dateien in 2 csv Dateien (wird normalerweise nicht benötigt) 

### create

Dieser Unterbefehl generiert CSV Dateien mit Metadaten für ein oder mehrere Objektverzeichnisse.

```
preprocess csv create [OPTIONS] AUSGANGSVERZEICHNIS
```

Geht rekursiv durch alle Verzeichnisse unterhalb von `AUSGANGSVERZEICHNIS`, prüft, ob es sich um ein
Objektverzeichnis handelt, und legt in jedem Objektverzeichnis zwei CSV-Dateien an: `object.csv` und 
`datastreams.csv`. Das Programm versucht dabei, so viele Werte wie sinnvoll möglich automatisch zu setzen,
indem es die vorhandenen Daten untersucht bzw. Werte aus der Projektkonfiguration (`project.toml`)
verwendet.
 
Dieser Befehl überschreibt keine bereits existierenden csv-Dateien, es sei denn, dass einer der Flags `--force-overwrite` oder `--update` genutzt wird (siehe unten).

#### Optionen

##### `-configfile`, `-c`  

Diese Option setzt den Pfad zur Projektkonfigurationsdatei (`project.toml`):

Beispiel:

```
preprocess csv create -c foo/bar/project.toml projects/myproject
```

Die Option braucht nur gesetzt zu werden, wenn sich die Konfigurationsdatei an einem außergewöhnlichen Ort befindet.
Im Normalfall kann der Speicherort der Datei automatisch ermittelt werden. Dabei gelten diese Regeln (in dieser Reihenfolge):

  1. Es wird überprüft, ob die Umgebungsvariable `GAMSCFG_PROJECT_TOML` gesetzt ist. 
  1. Falls die Umgebungsvariable nicht gesetzt ist, wird überprüft ob eine `.env` Datei 
     im aktuellen Ordner exisitiert und ob sie die Zeile `project_toml=` beinhaltet. 
  2. Falls keine dieser Optionen existiert wird nach einer `project.toml` in folgender Reihenfolge 
     gesucht: 
     
     - In dem Objektordner oder in einem übergeordneten Ordner des Objektordners 
     - Im aktuellen Verzeichnis. 

Falls dann noch immer keine Konfigurationdatei gefunden wurde, wird das Programm beendet.

##### `--force-overwrite`, `-f`

Ist diese Option gesetzt, werden allfällig bereits existierende CSV-Dateien ohne Rückfrage 
überschrieben. 

**!!! Achtung: Diese Option sollte nur mit großer Vorsicht verwenden werden, weil dadurch alle manuell 
veränderten oder ergänzten Eintragungen in den CSV Dateien verloren gehen !!!**

##### `-update`, `-u` 

Die Verwendung des Flags `--update` führt aktualisiert Einträge in den CSV-Dateien. Dies macht beispielsweise Sinn, wenn die Projektkonfiguration nachträglich geändert wurde, oder wenn nach der 
initialen Erzeugung der CSV-Dateien neue Datenströme angelegt wurden, die noch nicht in `datastreams.csv` enthalten
sind.

Dabei werden niemals Veränderungen an den Feldern `description`, `tags` oder `lang` vorgenommen. Felder, die automatisch von Dublin Core oder der Projektkonfiguration (.toml) übernommen werden können (`title`, `creator`, `publisher`und `rights`), werden aktualisiert. Das bedeutet, dass händisch vorgenommene Änderungen an diesen Felder überschrieben werden. Falls Sie diese Felder bereits händisch überarbeitet haben (was im Normalfall eher nicht der Fall sein wird), sollten sie evtl. zuvor mit `preproess csv collect` eine Excel oder CSV Datei mit den alten Werten erzeugen, damit Sie die Änderungen nach dem
Update überprüfen können. 


#####  ``--help`

Gibt den Hilfetext für `csv create` aus.

### collect

`preprocess csv collect` dient dazu, Daten aus den CSV-Dateien in den Objektordnern
einzusammeln und zusammen in eine Excel-Datei (`all_objects.xlsx`) zu speichern. 
Diese Excel-Datei sollte die Bearbeitung der Metadaten erheblich erleichtern und 
beschleunigen. Der Befehl `proprocess csv update` kann dann dazu verwendet werden, 
alle CSV Datei in den Objektordnern durch die Daten aus dem Excel-File neu zu generieren. 

Diese beiden Vorgänge können beliebig oft wiederholt werden. Da `all_objects.csv`  
jederzeit aus den Objekt-CSV-Dateien neu generiert werden kann, besteht keine Notwendigkeit,
die `all_objects.csv` Datei aufzubewahren, sobald ihre Inhalte via `preprocess csv update` 
in die Objekt-CSV-Dateien zurückgespielt worden sind.

Beispiel:

```
preprocess csv collect projects/myproject
```


#### Optionen

##### ``-output-dir <PFAD>`, `-o <PFAD>`

Diese Option erlaubt es, den Ordner festzulegen, in dem die Datei `all_objects.xlsx` (bzw. bei Verwendung
der Option `--to-csv` die beiden CSV-Dateien `all_objects.csv` und `all_datastreams.csv`) erzeugt werden.
Ist sie nicht gesetzt, wird das aktuelle Arbeitsverzeichnis verwendet.

##### `--to-csv`, `-c`

Ist diese Option gesetzt, erzeugt das Programm statt der Excel-Datei `all_objects.xlsx` zwei
CSV-Dateien: `all_objects.csv` und `all_datastreams.csv`. Die Verwendung dieser Option wird
nur benötigt, falls z.B. die Weiterverarbeitung der so generierten Datein im CSV Format einfacher ist.
Im Normalfall sollte sie nicht benötigt werden.

##### ``-help`

Gibt den Hilfetext für diesen Unterbefehl aus.

### update

`preprocess csv update` schreibt die in `all_objects.xslx` geänderten Daten wieder zurück in die 
`object.csv` und `datastreams.csv` der einzelnen Objektordner. Voraussetzung ist, dass
die Excel-Datei zuvor mit `preprocess csv collect` erzeugt worden ist. 
`csv update` ist also das Gegenstück zu `csv collect`: `csv collect` sammelt die Daten aus den
Objektverzeichnissen ein, `csv update` schreibt sie wieder dorthin zurück.

```
preprocess csv update [OPTIONS] PROJECTROOT
```

`PROJECTROOT` ist das Verzeichnis in dem die Objektordner liegen.

Beispiel:

```
preprocess csv update projects/myproject/objects
```

#### Optionen

##### `--input-dir`, `-i`

Diese Option bietet die Möglichkeit, den Ordner festzulegen, in dem `all_objects.xlsx` liegt. Diese Option muss
nur gesetzt werden, falls die Excel Datei nicht im aktuellen Arbeitsverzeichnis liegt.

##### `-from-csv`, `-c` 

Ist diese Option gesetzt, liest das Programm die gesammelten Daten nicht aus der Datei
`all_objects.xlsx`, sondern aus den beiden CSV-Dateien `all_objects.csv` und `all_datastreams.csv`.
Das macht nur Sinn, wenn zuvor bei `preprocess csv collect` die Option `--to-csv`verwendet wurde.

Falls diese Dateien nicht im aktuellen Arbeitsverzeichnis liegen, kann der Pfad zur korrekten
Verzeichnis mit der Option `--input-dir` gesetzt werden.

##### ``--help`

Gibt den Hilfetext für diesen Unterbefehl aus.
    
### csv2xslx

Dieser Befehl wandelt die beiden verpflichtend anzugebenen CSV Datein in eine Excel-Datei um.

*Im empfohlenen Workflow wird dieser Befehl nicht benötigt, weil der `collect` Unterbefehl
die Excel Datei direkt erzeugt.*

```
preprocess csv csv2xlsx [OPTIONS] <PFAD ZU OBJECT_CSV> <PFAD ZU DATASTREAMS_CSV>
```

Dieser Befehl erzeugt eine Datei `all_objects.xlsx` im aktuellen Arbeitsverzeichnis.

#### Optionen

##### ``--outputfile`, `-o`

Pfad zur zu erzeugenden xlsx-Datei. 
Standardmässig wird eine Datei  `all_objects.xlsx` im selben Verzeichnis erzeugt, in dem `all_objects.csv` liegt.


#####  ``--help`

Gibt den Hilfetext für diesen Unterbefehl aus.
       

### xlsx2csv

`preprocess csv xlsx2csv` wandelt eine xslx-Metadaten-Datei in zwei CSV Dateien um. 
Da die Excel Datei zwei Blätter (Tabellen) enthält (je eine für Objekte und Datenströme), werden zwei 
CSV-Dateien erzeugt.

*Im empfohlenen Workflow wird dieser Befehl nicht benötigt, weil die `collect` und
`update` Unterbefehle direkt auf der Excel Datei operieren können.*

```
preprocess csv xlsx2csv [OPTIONS] XLSX_FILE
```

wandelt `XLSX_FILE` in zwei Dateien `all_objects.csv` und `all_datastreams.csv` um. Diese werden im selben Verzeichnis
erzeugt, in dem auch `XLSX_FILE` liegt.

#### Optionen:

##### `--object-csv <PFAD ZUR ZU ERZEUGENDEN OBJECTS_CSV DATEI>`
        
Pfad zu der zu erzeugenden OBJECT_CSV Datei. Wird diese Option nicht gesetzt, wird eine Datei 'all_objects.csv' in dem 
Ordner erzeugt, in dem die xlsx-Datei (`XLSX_FILE`) gespeichert ist.

##### `--ds-csv` <PFAD ZUR ZU ERZEUGENDEN DATASTREAMS_CSV Datei>

Pfad zu der zu erzeugenden DATASTREAMS_CSV Datei. Wird diese Option nicht gesetzt, wird eine 
Datei 'all_datastreams.csv' in dem Ordner erzeugt, in dem die xlsx-Datei (`XLSX_FILE`) gespeichert ist.

##### `--help`

Gibt den Hilfetext für diesen Unterbefehl aus.

