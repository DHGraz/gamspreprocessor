# Objektverzeichnisse

Der Ingest in GAMS erfolgt über 
[BagIt](https://datatracker.ietf.org/doc/html/rfc8493) 
basierte Pakete. Jedes Paket enthält genau ein digitales Objekt.
Ein solches Bag ist also ein SIP im Sinne von OAIS.

Die direkte, d.h. manuelle Erstellung dieser *Bags* wird nicht empfohlen. 
Auch die nachträgliche Bearbeitung von Daten in existierenden Bags empfiehlt
sich nicht, da jede Änderung an den Daten unter anderem dazu führt, dass neue
Prüfsummen generiert werden müssen.

Der empfohlene Weg zur Erstellung von Bags führt über Objektverzeichnisse. Das
sind Verzeichnisse im Filesystem, die einem bestimmten Aufbau folgen und als 
Ausgangspunkt für die Erzeugung der BagIt Bags dienen. Ein Hilfsprogramm 
namens `packager` wandelt dann die Objektverzeichnisse in ingestierfähige 
Bags um.

## Aufbau eines Objektverzeichnisses

Die Form der Objektverzeichnisse wurde bewusst einfach gehalten. 
Jedes Objektverzeichnis muss aber folgende Voraussetzungen erfüllen:

  - Der Verzeichnisname MUSS der ID (PID) des Objekts entsprechen. Dabei sind bestimmte, weiter unten
    beschriebene Regeln zu befolgen.
  - Jedes Objektverzeichnis MUSS eine Datei `DC.xml` mit den inhaltlichen Metadaten enthalten.
  - Jedes Objektverzeichnis MUSS zwei CSV Dateien mit zusätzlichen Metadaten enthalten:
    -  `object.csv` enthält zusätzliche Metadaten zum Objekt
    -  `datatstreams.csv` enthält zusätzliche Metadaten zu jeder zu ingestierenden Datei.
    Diese beiden Datein können mit dem Unterbefehl [preprocess csv](subcommands/csv.md) weitgehend automatisch erzeugt und verwaltet werden.
  -  Eine beliebige Menge von Dateien ("Datenströmen"), wobei nur jene Dateien ins SIP-Package aufgenommen werden, für die ein
     Eintrag ind `datastreams.csv` existiert. 

Ein prototypisches Objektverzzeichnis könnte also so aussehen:

```
foo.1
|
|-- DC.xml
|-- datastreams.csv
|-- object.csv
|-- foo.xml
|-- fol1r.jp2
|-- fol1v.jp2
```

## PIDs und Verzeichnisnamen

Wie bereits beschrieben, MUSS der Verzeichnisname der Objekt ID (PID) 
entsprechen. 
Jeder Name (und somit jede Objekt ID) besteht aus zwei bzw. drei Teilen:

```
[Typ-Präfix:]<Projekt ID>.<Objektbezeichnung>
```

Die `Projekt ID` und die Objektbezeichnung sind verpflichtend, das Typ-Präfix 
ist ein optionales Relikt aus GAMS 3 Zeiten und sollte für 
neue Projekte nicht mehr verwendet werden. Falls ein Typ-Präfix verwendet wird,
MUSS der Doppelpunkt im Verzeichnisnamen durch `%3A` ersetzt werden!

Hier eine paar Beispiele für vollständige Objekt IDs:

  * `foo.1`
  * `foo.img1`
  * `foo.img-1`
  * `foo.img.1`
  * `o:foo.1` (nicht empfohlen). Der Name des Objektverzeichnisses muss in diesem Fall `o%3Afoo.1` lauten!

### Erlaubte Werte für Typ-Präfixe

Falls ein Typ-Präfix verwendet werden soll (nicht empfohlen!), ist nur einer diese Werte erlaubt:
        `collection`, `container`, `context`, `corpus`, `o`, `podcast`, `query`

### Erlaubte Zeichen für die Projekt ID

Projektkürzel (also der Teil vor dem Punkt) dürfen nur aus ASCII-Kleinbuchstaben und Ziffern bestehen,
wobei das erste Zeichen ein Kleinbuchstabe sein MUSS.

Valide Projektkürzel sind also `foo` oder `foo123`.

Nicht erlaubte Projektkürzel sind zum Beispiel:

  * `Foo` (Großbuchstabe)
  * `foo-bar` (Nicht erlaubtes Zeichen `-`)
  * `1foo` (Ziffer an erster Stelle)
  * `bäh` (Verwendung eines nicht ASCII-Zeichens)

###  Erlaubte Zeichen in der Objektbezeichnung

Die eigenliche Objektbezeichnung steht nach einem Punkt als Trennzeichen und 
darf nur folgende Zeichen enthalten:

  * ASCII-Buchstaben (nur Kleinbuchstaben erlaubt: a-z, keine Umlaute und sonstige Sonderzeichen)
  * Ziffern
  * `-` (Minus) und `.` (Punkt)
    
Erlaubte Objektbezeichnungen sind somit beispielsweise: `1`, `a` oder `foo-bar.1`

Nicht erlaubte Objektbezeichnungen sind:
      
  * `Foo` (Großbuchstabe)
  * `foo_bar` (Nicht erlaubtes Zeichen: Underscore)
  * `bäh` (Umlaut)
  

## Erzeugung von Objektverzeichnissen

Die Generierung von Objektverzeichnissen kann auf beliege Art erfolgen. 
Manche Projekte verwenden selbst geschriebene Scripte umd die benötigten Objekte 
z.B. aus Google Spreadsheets, XML Dateien usw. zu erzeugen.

Der `preprocessor`stellt den Unterbefehl `splitproject` bereit, der Daten, wie sie 
typischerweise in alten GAMS Projekten angelegt wurden,
in einzelne Objektordner aufdröselt.


## Verwaltung von Objektverzeichnissen

TODO: init, csv, 
