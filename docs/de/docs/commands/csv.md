Comments marked with ###COMMENT###


# CSV

Hilfsfunktionen mit denen die CSV Dateien mit den Objekt-Metadaten erzeugt und verwaltet werden könne.

## Verwendung 

```
preprocess csv [OPTIONS] COMMAND [ARGS]
```

## Unterbefehle

* `preprocess csv collect` Sammelt Daten von allen CSV Dateien in allen Objektordnern
* `preprocess csv create` Generiert CSV Dateien mit Metadaten für Objektverzeichnisse
* `preprocess csv csv2xslx` Konvertiert CSV-Dateien in XLSX-Dateien
* `preprocess csv xlsx2csv` Konvertiert XLSX-Dateien in 2 csv Dateien 
* `preprocess csv update` Aktualisiert Objekt- und Datenstrom CSV Dateien anhand der gesammelten CSV Dateien

### preprocess csv collect

`preprocess csv collect` Sammelt Daten aus allen CSV-Dateien in allen Objektordnern

```
preprocess csv collect [OPTIONS] OBJECTS_DIR
```
* Sammelt alle Daten in 'object.csv' und 'datastrams.csv' Dateien innerhalb von 'objects-dir' in einer 'all_objects.xlsx' Datei
* Wenn die Option `--to-csv` gesetzt wird, werden statt einer XLSX Datei zwei CSV-Dateien erzeugt, 'all_objects.csv' und 'all_datastreams.csv'
* Ohne Angaben eines Ausgabeordners `--output-dir` werden Dateien im aktuellen Arbeitsverzeichnis erstellt
* Optionen:
    * -o, --output-dir TEXT   Pfad zum Ausgabeverzeichnis. Standard: aktuelles Arbeitsverzeichnis
    * -c, --to-csv            Gibt CSV-Dateien statt einer Excel-Datei aus.
    * --help                  Gibt Hilfe für -collect aus

### preprocess csv create
`preprocess csv create` Generiert CSV Dateien mit Metadaten für Objektverzeichnisse

```
preprocess csv create [OPTIONS] PROJECTROOT
```
* Generiert eine 'object.csv' und eine 'datastreams.csv' Datei für jedes Objektverzeichnis in oder unter dem Wurzelverzeichnis. Das bedeutet, dass dieser Befehl sowohl auf einzelnen Objektverzeichnisse als auch auf Projektverzeichnisse mit mehreren Objektverzeichnissen angewendet werden kann.
* Dieser Befehl überschreibt keine bereits existierenden csv-Dateien, es sei denn die Flag `--force-overwrite` oder `--update` wird genutzt
* Die Flag `--force-overwrite`  überschreibt alle exisitierenden csv-Dateien. Alle exisitierenden Metadaten werden gelöscht. Die Nutzung der Flag ist also nur sinnvoll, wenn die Metadaten komplett neu angelegt werden sollen. 
* Die Verwendung des Flags `--update` führt dazu, dass die Daten für bestimmte Felder aus den vorhanden csv-Dateien zusammgengeführt werden. Dies ist sinnvoll, wenn Metadaten geupdatet werden sollen nachdem Datastreams hinzugefügt wurden oder wenn sich Projektkonfigurationen geändert haben. Es werden keine Veränderungen an den Feldern 'description', 'tags' oder 'lang' vorgenommen. Aber Felder, die automatisch von Dublin Core oder der Projektkonfiguration (.toml) übernommen werden können, werden angepasst. Wenn jedoch Veränderungen an 'title', 'creator', 'publisher' oder 'rights' vorgenommen wurden, sollte dieser Befehl nur nach vorherigem Absichern vorgenommen werden. Falls keine neuen Werte gefunden werden können, bleibt das existierende Feld unverändert.  
* Optionen: 
    * -c, --configfile TEXT     
        Pfad zur Projektkonfiguration (.toml). Wenn dieser Pfad noch nicht gesetzt wurde, wird überprüft, ob die Variable 'GAMSCFG-PROJECT-TOML' gesetzt wurde. Falls nicht, wird überprüft ob eine '.env' Datei im aktuellen Ordner exisitiert und ob sie die Zeile 'project_toml=' beinhaltet. Falls keine dieser Optionen existiert wird nach einer 'project.toml' in folgender Reihenfolge gesucht: 1) In dem Objektordner oder im übergeordneten Ordner des Objektordners, 2) im aktuellen Verzeichnis. Falls keine toml-Datei gefunden werden kann, scheitert dieser Befehl. 
    * -f, --force-overwrite 
        Überschreibt die existierenden csv-Dateien. Nur mit großer Vorsicht verwenden, weil alle manuell veränderten Metadaten verloren gehen.
    * -u, --update 
        Updated alle exisiterenden csv-Dateien
    * --help
        Gibt Hilfe für create aus

    
### preprocess csv csv2xslx

`preprocess csv csv2xslx` Wandelt csv-Dateien in xlsx-Dateien um

```
preprocess csv csv2xlsx [OPTIONS] OBJECT_CSV DS_CSV
```

* Umwandlung von ausgewählten csv-Dateien in xlsx-Dateien  ###COMMENT werden ALLE Dateien umgewandelt oder nur ausgewählte?###
* Optionen: 
    * -o, --outputfile TEXT
        Pfad zur ausgegebenen xlsx-Datei. Standard ist 'all_objects.xlsx' im Ordner in dem 'all_object.csv' ausgelesen wurde ###COMMENT Ich glaube, das ist ein Typo und es müsste 'all_objects.csv' sein, weil das in den anderen Befehlen so vorkommt###
    * --help
        zeigt Hilfe für diesen Befehl an

### preprocess csv xlsx2csv

`preprocess csv xlsx2csv` Wandelt eine xslx-Metadaten-Datei in 2 csv-Dateien um ###COMMENT Warum sind das zwei csv Dateien? Sollen wir das dazu schreiben?###

```
preprocess csv xlsx2csv [OPTIONS] XLSX_FILE
```
* Umwandlung einer ausgewählten xlsx-Datei in 2 csv-Dateien
* Optionen:
    * --object-csv TEXT
        Pfad zu der ausgegbenen csv-Datei. Standard ist 'all_objects.csv' im Ordner, in dem die xlsx-Datei gespeichert ist
    * --ds-csv TEXT
        Pfad zu den ausgegebenen Datastreams csv-Dateien. Standard ist 'all_datastreams.csv' im Ordner in dem die xlsx-Datei gespeichert ist
    * --help
        zeigt Hilfe für diesen Befehl an

### preprocess csv update

`preprocess csv update` Updated die Objekt- und Datastream-csv-Dateien aus den gesammelten csv-Dateien

```
preprocess csv update [OPTIONS] PROJECTROOT
```

* Updated die Objekt- und Datastream-csv-Dateien aus den gesammelten csv-Dateien
* Dies ist das Gegenstück zum `-collect` Befehl. `-update` liest Daten aus 'all_objects.xlsx' aus und updated 'object.csv' und 'datastreams.csv' in jedem Objektordner
* `--from-csv` liest aus 'all_objects.csv' und 'all_datastreams.csv' anstatt aus der xlsx-Datei
* Falls kein 'input_dir' angegeben wurde, wird erwartet, dass alle Dateien im aktuellen Ordner sind.
* Optionen:
    * -i, --input-dir TEXT
        Pfad zu dem Ordner, in dem sich die gesammelten csv-Dateien befinden. Dies ist der selbe Ordner, der auch mit '--output-dir' im `-collect` Befehl gesetzt wurde. Standard ist das Wurzelverzeichnis des Projekts
    * -c, --from-csv
        Liest aus der csv-Datei anstatt aus der xlsx
    * --help 
        Zeigt Hilfe für diesen Befehl an