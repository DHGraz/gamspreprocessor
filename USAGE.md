# PREPROCESSING AND PACKAGING

## Setup von Python und Virtual Environement mit *Windows*

- Python 3.12.x aus dem **Windows Store** installieren
  Aktuell wird Version 3.12.x empfohlen
- in der **Powershell** die Python-Version prüfen: `python --version`
- in der **Powershell**: Virtual environment anlegen: `python -m venv .venv`
- in der **Powershell**: Virtual environment aktivieren: `.\.venv\Scripts\activate`


## gamspreprocessor und gamspackager installieren
- `pip install gamspreprocessor-x.y.z.tar.gz`
- `pip install gamspackaging-x.y.z.tar.gz`
- die Pakete gamspreprocessor und gamspackaging werden später über PyPi zur Verfügung gestellt


## Verzeichnis für Projekt anlegen
- in der Powershell:
  - `mkdir <projektkuerzel>`
  - `cd <projektkuerzel>`


## Projekt initialisieren
- im Verzeichnis `<projektkuerzel>`:
  - `preprocess project init`
  - legt an:
    - `project.toml`
    - `.gitignore`
    - `objects` Verzeichnis
  - händisch lokal ein `bags` Verzeichnis anlegen. Dieses kann im Prinzip überall
    liegen. Nin nicht sicher, ob der Projektordner dafür optimal ist, weil es ja quasi
    ein Zwischenschritt ist, der jederzeit wiederholt werden kann.

- Verzeichnisse:
```
<projektkuerzel>
├── bags
├── objects
└─ project.toml
```

## `project.toml` bearbeiten
- nur die Felder in der Sektion `[metadata]` müssen korrekt ausgefüllt werden

### `project.toml` aktualisieren

Solange das Format für `project.toml` noch nicht stabil ist, empfiehlt es sich,
nach dem Installieren einer neuen Version vom Packager diesen Befehl laufen zu lassen:

```
preprocess project update <Pfad zum project.toml>
```

Dadurch wir das existierende `project.toml` auf das aktuelle Format umgebaut.
Existierende, noch benötigte Einträge werden dabei nicht verändert.

## `objects` Verzeichnis
- im Verzeichnis `objects` muss für jedes Digitale Objekt
  ein Unterorder angelegt werden, der als Namen den PID des
  Objekt hat!
- in den jeweiligen Objektordner die TEIs und die dazugehörige Dateien
  (z.B. Bilder usw.) ablegen


## Dublin Core
- `DC.xml` muss für jedes digitale Objekt erzeugt werden. Enthält ein 
  Objektverzeichnis kein `DC.xml`, wird es bei allen folgenden Schritten ignoriert.
- Für Objekte mit XML-basierten Datenströmen wie TEI oder LIDO kann das DC.xml 
  auf bekannte Weise via XSLT erzeugt werden. (Bei Bedarf können weitere 
  Transformationszenarien hinzugefügt werden).
  Grundsätzlich gilt: Mindestens der Titel (`dc:title`) muss auf Englisch sein und 
  das Attribut `xml:lang="en"` enthalten.
  
  - Um ein `DC.xml` für ein einzelnes Objekt zu erzeugen:
    
    ```
    preprocess transform xslt -x project.xsl foo/TEI.xml foo/DC.xml
    ```

    `project.xsl` ist hier die XSLT-Datei, die z.B. TEI nach DC transformiert.

  - Will man das xslt auf mehr als ein Objekt anwenden, muss statt
    `transform` `multitransform` verwendet werden:

    ```
    preprocess multitransform xslt -r -x project.xsl -o DC.xml -p 'S*.xml' objects
    ```
    Bestimmte Dateinamen (z.B. 'DC.xml') können über die Option `--exclude` oder kurz `-e`)
    aus dem Muster ausgenommen werden. `--exclude` kann mehrfach angegeben werden:

    ```
    preprocess multitransform xslt -r -x project.xsl -o DC.xml -p '*.xml' -e DC.xml -e foo.xml objects
    ```

    transformiert alle gefundenen `*.xml` Dateien, nicht jedoch `DC.xml` und `foo.xml`.
    
    Soll die Transformation nur auf eine Verzeichnisebene angewendet werden, kann
    das `-r` weggelassen werden. `-o` legt die Ausgabedatei für jedes Objektverzeichnis
    fest, `-p` definiert ein Muster für die zu verarbeitenden Dateien: `S*.xml` würde
    als das XSLT auf alle XML-Datei, der Name mit `S` beginnt angewendet. Vorsicht:
    Das Muster muss pro Objektverzeichnis eindeutig sein, damit jeweils nur eine Datei
    transformiert wird. `objects` ist das Verzeichnis in dem nach zu verarbeitenden Dateien
    gesucht wird.

    Alternativ kann man zuerst z.B. mit `find` eine Liste von Dateien in eine
    Datei schreiben (eine Datei pro Zeile) und dann diese Datei übergeben:

    ```
    preprocess multitransform xslt -x project.xsl -o DC.xml -l files_to_process.txt objects
    ```



## CSV bzw. Excel-Dateien erzeugen

Der Packager erwartet in jedem Objekt-Verzeichnis zwei Dateien mit
zusätzlichen Metadaten:

  - object.csv
  - datastreams.csv

Diese Dateien können im Prinzip händisch geschrieben werden. Der empfohlene
Weg ist aber, die Dateien teilautomatisiert erzeugen zu lassen:

```
preprocess csv create <folder>
```

Dieser Befehl kann selektiv für einzelne Objektfolder ausgeführt werden, im
Normalfall lässt man ihn gegen alle Objektfolder unter einem Pfad (wie z.B.
`objects\') laufen:

```
preprocess csv create objects
```

Dadurch werden die beiden CSV-Dateien in jedem darunter liegenden Objektverzeichnis erzeugt.

Falls die CSV-Dateien für ein Objektverzeichnis bereits vorhanden sind, werden sie nicht
verändert. Dieses Verhalten kann durch Optionen verändert werden:

  - `--update` führt bestehende CSV-Daten mit einer veränderten Projektkonfiguration
     oder nachträglich ergäntzten Datenströmen zusammen. Wenn Sie also Änderungen
     in `project.toml` gemacht haben oder neue Datenströme in einem Objektverzeichnis
     angelegt haben, sollten Sie `preprocess csv create --update <folder>` laufen
     lassen.
  - `--overwrite`.  Das ist eine gefährliche Operation, die alle bereits bestehenden 
     CSV-Dateien überschreibt. Sie sollte nur verwendet werden, wenn Sie wieder von
     ganz vorne beginnen möchten.

Die so generierten Dateien sind jedoch nur so weit automatisch befüllt, wie dies
z.B. aus der Projektkonfiguration ableitbar ist. Die einzelnen CSV-Dateien müssen also
händisch nachbarbeitet werden. Damit dies möglichst effizient erfolgen kann,
empfehlen wir diesen Weg:

  - `preprocess csv collect <objects-root>`. `objects-root` ist dabei der Pfad zu dem Ordner,
    in dem die Objektverzeichnisse liegen, deren CSV-Dateien eingesammelt werden sollen.
    Dieser Befehl  generiert im aktuellen Verzeichnis eine Datei `all_objects.xlsx`im Excel-Format mit 2 Tabs:
    einer enthält alle Daten auf allen eingesammelten CSV Dateien, der zweite die
    Daten aus allen eigensammelten Datenstrom-Dateien.
    Diese Sheets können nun bearbeitet werden, was wegen der von Excel bereit gestellten
    Möglichkeiten die Bearbeitung massiv erleichtern sollte:
      * Hinkopieren von Werten in viele Felder
      * Umsortieren von Zeilen um z.B. fehlende Werte und 'Ausreisser' einfach zu finden
      * ...
  - Wenn die Bearbeitung der beiden Sheets beendet ist, können die Daten wieder
    in die einzelnen CSV Dateien zurückgespielt werden:
    `preprocess csv update <objects-root`. Falls `all_objects.csv` nicht gefunden
    wird, müssen Sie die `--input-dir` Option verwenden, die auf das Verzeichnis verweist,
    in dem das Excel File liegt: preprocess csv update --input-dir <verzeichis> <objects-root`.



## Bags erzeugen
- sind alle obigen Anpassungen erfolgt, können Bags von den Objekten erzeugt werden
- `packager bag create <root-folder|projektkuerzel> -o <bag-folder>`, z.B. Bags für das
  Projekt 'hsa': `packager bag create hsa -o bags`
