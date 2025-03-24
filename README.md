# Gamspreprocessor

## Überblick

Gamspreprocessor ist eine Sammlung von Werkzeugen zur Vorbereitung von
Gams-Ingests, die zu einem Befehl (`preprocess`) zusammengefasst wurden.

- mit Hilfe von `splitproject` kann versucht werden aus vorhanden Verzeichnissen
  Objekt-Ordner zu erzeugen (z.B. von `Y:\data\projekte\...`)
- erzeugt mit entsprechenden XSLTs fehlende `DC.xml` für jedes Objekt(verzeichnis)
- erzeugt Excel- bzw. CSV-Dateien (`object.csv`, `datastreams.csv`)


Für ``preprocess`` selbst und für alle Unterbefehle gibt es die '--help' 
Option, die alle Möglichkeiten auflistet. 

``preprocess`` unterstützt diese globalen Optionen:

  * ``--logfile`` Ist diese Option gesetzt, wird zusätzlich zur normalen
    Ausgabe am Bildschirm eine Log-Datei mit dem Wert dieser Option angelegt. 
  * ``--filelog-level`` Es ist möglich, für die Logdatei ein anderes
    Loglevel einzustellen. Damit kann z.B. die Debug-Ausgabe in die Datei
    geschrieben werden, während die Ausgabe am Bildschirm weniger Ausgabe
    generiert. Der Wert dieser Option muss einer der folgenden Werte sein 
    und überschreibt den Wert im `project.toml`:

    - DEBUG
    - INFO
    - WARNING
    - ERROR
    - CRITICAL
  
    Groß- und Kleinschreibung spielt dabei keine Rolle.

  - ``--verbose`` (``-v``) Die Option setzte die Ausgabe auf DEBUG. Sie kann
    nicht zusammen mit ``--quiet`` verwedendet werden.  
  - ``--quiet``(``-q``) Diese Option minimiert die Ausgage auf 
    Fehlermeldungen. Sie kann nicht zusammen mit ``--verbose`` verwendet 
    werden. 
  - ``--version`` Gibt die Version von ``preprocess`` aus.
  - ``--help`` Gibt den Hilfetext für ``preprocess`` aus.

Aktuell sind diese Unterbefehle implementiert:

  - splitproject
  - transform
  - multitransform
  - csv create

### splitproject

```mermaid
graph LR
    subgraph A[Projektverzeichnis]
    AA[Enthält z.B. TEI, LIDO-Files,
    mit referenzierten Dateien
    wie z.B. Bilder usw.]
    end
    subgraph B[Objektverzeichnis]
    BB[Enthält Dateien, die
    beim Preprocessing
    weiterverarbeitet werden,
    um Bags für den Ingest zu
    erzeugen]
    end
    A --> |splitproject| B[Objektverzeichnis]
```

``preprocess splitproject`` wird dazu verwendet, bestehende Projektstrukturen
(wie in GAMS 3) so umzubauen, dass für jedes Objekt und seine Datenströme
ein eigenes Verzeichnis angelegt wird. Aktuell werden basale TEI und LIDO
Objekte unterstützt. 

``splitproject`` kann nicht direkt verwendet werden sondern erwartet einen
weiteren Unterbefehl: 
- ``split`` erzeugt die Objektverzeichnisse, 
- ``showunhandled`` zeigt alle Dateien, die im Ursprungsverzeichnis vorhanden sind,
aber noch in keinem Objektverzeichnis verwendet werden. Dieser Subbefehl
ist somit ein wichtiges Werkzeug, mit dem verhindert werden kann, dass Dateien
beim Aufsplitten von Objekten verloren gehen.

#### split
``split`` erwartet als Argument eine Liste von umzuwandelnden Dateien.
Das sind jeweils die für das Objekt zentralen Dateien. Im Normalfall liefert -
sofern Wildcards verwendet werden - die Shell eine entsprechende Liste. 

```sh
preprocess splitproject split '*TEI*.xml'
```

Es können aber auch eine Reihe von Dateien, jeweils durch ein Leerzeichen
getrennt, angegeben werden. 

```sh
preprocess splitproject split TEI_1.xml TEI_2.xml TEI99.xml
```

Eine weitere Möglichkeit, bei der dann kein Argument anzugeben ist, 
besteht in der Verwendung der ``--file-list`` Option:

```sh
preprocess splitproject split --file-list files_to_convert.txt
```

``split`` kennt diese Optionen:

  - ``--output-dir`` Über diese Option kann das Verzeichnis festgelegt werden,
    in dem die Objekt-Verzeichnisse erzeugt werden. Wird die Option nicht
    verwendet, nimmt der Splitter ein Verzeichnis ``objects``direkt
    unterhalb des aktuellen Verzeichnisses an. Das angegebene Verzeichnis **muss
    bereits existieren**, wird also nicht automatisch angelegt.
  - ``object-format`` Erlaubt zur Zeit einen dieser Werte: ``auto`` (default),
    ``lido`` oder  ``tei``. Die explizite Festlegung des Typs sollte so gut wie
    nie nötig sein. *Ich überlege deshalb, diese Option wieder zu entfernen oder
    als Filter für Dateitypen zu verwenden.*
  - ``--file-list`` erwartet als Wert den Pfad zu einer Datei, in der
    die "Hauptdateien" gespeichert sind, nach denen gesplittet werden
    soll. Die Verwendung dieser Option ist eine Alternative zur 
    Auflistung der zu verarbeitenden Dateien auf der Kommandozeile
    (``SOURCEFILES``).
    Man kann also eine Liste der "Objektdateien" vorgenerieren (z.B. mit 
    ``find``) und diese Liste (eine Datei pro Zeile) an den Splitter
    übergeben. Die Option kann nicht zusammen mit dem Argument ``SOURCEFILES``
    verwendet werden.
  - ``--replace`` überschreibt keine existierenden 
    Objektverzeichnisse. Durch das Setzen der ``--replace`` Option wird
    dieses Verhalten so verändert, dass bereits existierende 
    Objektverzeichnisse gelöscht und neu angelegt werden.
  - ``--reset`` Dieser Flag stellt den BookKeeper auf den Ausgangszustand zurück. 
    Diese Option sollte nur dann eingesetzt werden, wenn man alle Ordner
    unterhalb von ``--output-dir`` gelöscht hat und das Aufsplitten  in
    Projekte von vorne beginnen möchte. Diese Option setzt nur den
    BookKeeper zurück, löscht aber keine bereits erzeugten #
    Objektverzeichnisse.
  - ``--help`` zeigt die vom Unterbefehl bereitgestellten Argumente und Optionen



#### showunhandled

Dieser Unterbefehl zeigt alle Dateien, die zwar im oder unterhalb des
Ausgangsverzeichnisse vorhanden sind, jedoch in keinem Objektverzeichnis
verwendet werden. Er ist also ein wichtiges Werkzeug, um sicherzustellen,
dass der Splitter alle vorhandenen Dateien verarbeitet hat.

Der Aufruf erwartet den Pfad zum Wurzelverzeichnis der Objektverzeichnisse
(das ist der Pfad, der als Option ``--output-dir`` bei ``split`` verwendet
wurde) als Argument:

```sh
preprocess splitproject showunhandled <Pfad>
```

Der Befehl kennt keine Optionen außer ``--help``.

### transform und csv create

```mermaid
graph LR
    subgraph A[Projektverzeichnis]
    AA[Pro Objekt ein Verzeichnis mit 
    z.B. TEI, LIDO-Files,
    mit referenzierten Dateien
    wie z.B. Bilder usw.]
    end
    subgraph B[Dublin Core]
    BB[erzeugt pro Objektverzeichnis
    ein DC.xml]
    end
    subgraph C[Objektverzeichnis]
    CC[erzeugt CSV bzw. Excel-Dateien
    für object.csv und
    datastreams.csv]
    end
    A --> |transform| B[Objektverzeichnis]
    B --> |csv create| C[Objektverzeichnis]
```


In der aktuellen Version unterstützt ``transform`` nur eine Art von Transformation: ``xslt``.
Dabei wird im Hintergrund ``saxon`` verwendet. Die verwendete Saxon-Version kann mit dem
Befehl

```sh
preprocess transform saxon-version
```

ermittelt werden.

#### transform xslt: erzeugen von DC.xml

Der ``xslt`` Befehl von Transform wendet eine XSLT Datei auf eine oder mehrere XML Dateien an:

```sh
preprocess transform xslt -x myxslt.xsl -o DC.xml foo/TEI.xml
```

wendet ``myxslt.xsl`` auf ``foo/TEI.xml`` an und schreibt die Ausgabe in die Datei
``foo/DC.xml``

Gibt man mehr als eine XML-Datei an (oder verwendet ein File-Pattern, das die Shell expandiert),
wird die XSLT-Datei auf alle XML-Dateien angewendet. Die erzeugte Ausgabe wird dabei jeweils
in das Verzeichnis geschrieben, in dem die originale XML Datei liegt.

```sh
preprocess transform xslt -x myxslt.xsl -o DC.xml foo/TEI.xml bar/TEI.xml
```

Erzeugt zwei neue Dateien: ``foo/DC.xml`` und ``bar/DC.XML``.

Alternativ zur Angabe von XML-Datei, können die zu transformierenden XML-Datei (mit Pfad)
zeilenweise in eine Datei geschrieben werden:


```sh
foo/TEI.xml
bar/TEI.xml
```

Diese Datei kann mit der ``-file-list`` (oder ``-l``) Option bekannt gemacht werden.
Nehmen wir an, dass die entsprechende Datei als ``xmls_to_process.txt`` abgespeichert
wurde. Dann kann sie so verwendet werden:

```sh
preprocess multitransform xslt -r -x myxslt.xsl -p 'TEI*.xml' -o DC.xml -l objects
```

## project.toml

Um die Metadaten-CSV-Dateien zu erstellen, benötigt der Preprocessor Daten über das Projekt, 
zu dem die Objekte gehören.
Diese Infos müssen in einer Konfigurationsdatei mit dem Namen `project.toml` bereitgestellt werden.
Mit der Option `-c` von `packager create csv`, kann auch ein anderer Dateinamen verwendet werden, 
wir empfehlen jedoch, `project.toml` zu verwenden.

Die Datei muss den Regeln des TOML-Formats folgen (https://toml.io). Derzeit ist
die Datei sehr einfach, da sie nur aus wenigen Elementen besteht. Hier ist ein Beispiel für das Projekt `hsa`:

```
[metdata]
project_id = "hsa"
creator = "Gams HSA Project"
publisher = "Gams"
rights = "Creative Commons Attribution-NonCommercial 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)"

[general]
desid_keep_extendsion = true
loglevel = "info"
```

Eine `project.toml` kann entweder händisch oder mit Hilfe der [`gamslib`](https://zimlab.uni-graz.at/gams5/production/gamslib) angelegt werden.
Die Toml-Datei **muss** die o.g. Felder enthalten.

Nur die Einträge im Abschnitt 'metdata', werden für die Metadaten-Extraktion in die CSV-Dateien verwendet.

## Dublin Core (DC.xml)

- DC.xml **muss** vorhanden sein
- kann z.B. mit Hilfe eines XSLTs auf TEI erzeugt werden (s. gamspreprocessor)
- muss folgende Felder enthalten:
  - identifier
  - title
  - creator
  - rights
- kann zusätzlich weitere Felder enthalten wie bspw.
  - date (im ISO-Format?)
  - location 
  - ... (s. [DC Template](https://zimlab.uni-graz.at/gams/metadata/templates/dc_template.xml))

## csv create: CSV bzw. Excel-Dateien erzeugen
```sh
preprocess csv create <path-to-object-root-folder>

```

## CSV erzeugen 

Es werden zwei CSV-Dateien im Projektordner erzeugt:

  * object.csv
  * datastreams.csv

Die Idee dahinter ist, die vom SIP benötigten und nicht automatisch ermittelbaren Metadaten so weit wie möglich vorzugenerieren.
Der Curator hat dann die Möglichkeit, diese Daten noch einmal zu überarbeiten und zu ergänzen, ehe sie als Ausgangspunkt
für die Erzeugung des SIP verwendet werden. Diese beiden Dateien landen nicht im SIP
(s.a. [packager](https://zimlab.uni-graz.at/gams5/production/packaging)).

Die Logik bei Generierung der Objektmetadaten ist diese (die Zahlen geben die Reihenfolge an, wie die
Daten ermittelt werden):

| Key         | Beschreibung        |    DC.xml        | toml | Defaultwert | User |
|-------------|---------------------|------------------|------|-------------|------|
| recid       | Pid DigObj          | -                | -    | 1 (=PID)    | 3    |
| title       | Titel DigObj        | 1 (dc:title)     | -    | 2 (=PID)    | 3    |
| project     | Projektkürzel       | -                | 1    | 2 ("")      | 3    |
| description | Beschr. DigO (opt.) | 1                | -    | 2 ("")      | 3    |
| creator     | Projektkürzel?      | -                | 1    | 2 ("")      | 3    |
| rights      |                     | 2 (dc:rights)    | 1    | 3 CC BY-NC  | 4    |
| publisher   | Projleiter? GAMS?   | 2 (dc:publisher) | 1    | 3 ("")      | 4    |
| source      | Quelle              | -                | -    | 1 "local"   | 2    |
| objectType  |                     | -                | -    | 1 "text"    | 2    |
| mainResource| Hauptdatenstrom     | -                | -    | 1 ""        | 4    |
| funder      | Fördergeber         | -                | 1    | 1 ""        | 2    |


Die Logik bei Generierung der Datenstrommetadaten ist diese (die Zahlen geben die Reihenfolge an, wie die
Daten ermittelt werden):


| Key         | Beschreibung       | auto |object | Defaultwert  | User |
|-------------|--------------------|------|-------|--------------|------|
| dsid        | Data Stream ID     |   1  |  -    | -            |  -   |
| dspath      | Path to data stream|   1  |  -    | -            |  -   |
| mimetype    | type of DS         |   1  |  -    | -            |  -   |
| title       |                    |   -  |  -    | 1 ("")       |  2   |
| description | Optional           |   -  |  -    | 1 ("")       |  2   |
| creator     |                    |   -  |  -    | 1 ("")       |  2   |
| rights      | use obj rights?    |   -  |  1    | 2 (CC BY-NC) |  3   |
| lang        | lang des DS        |   2  |  -    | -            |  3   |
| tags        | user defined tags  |   -  |  -    | -            |  3   |
