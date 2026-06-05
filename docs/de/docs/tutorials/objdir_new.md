# Objektverzeichnisse für neue Projektdaten

Liegt ein neues Projekt an, können die Objektverzeichnisse direkt erzeugt werden. 
Die einfachste Möglichkeit ist, für jedes Objekt ein neues Verzeichnis anzulegen.

## Objektverzeichnisse

Der Name des Verzeichnisses MUSS der Objekt-ID (PID) entsprechen.
Ein neues Objekt mit dem PID `foo.bar.1` muss daher in einem gleichnamigen 
Ordner angelegt werden. 

Die bisher verwendeten Prefixe wie `context:` oder `o:` werden nicht mehr empfohlen,
können aber weiterhin verwendet werden. Zu beachten ist dabei jedoch, dass der
Doppelpunkt kein erlaubtes Zeichen in Dateinamen für Objektverzeichnisse darstellt
und als `%3A` kodiert werden muss. 

Der Objekt `o:foo.bar.1` muss also im Ordner `o%3Afoo.bar.1` angelegt werden.
Im Zweifelsfall deshalb vielleicht doch auf das
Präfix verzichten.

## Datenströme

Die Datenströme eines Objekt werden dann einfach im Objektverzeichnis als Dateien abgelegt. 
Der Dateiname entspricht dabei der Datenstrom ID. Groß- und Kleinschreibung wird übernommen.

Datenströme in Unterverzeichnissen des Objektordners sind zwar grundsätzlich möglich, 
werden aber beim Erzeugen des SIP eliminiert. Ein Datenstrom der im Objektverzeichnis als
`foo.bar.1/images/img1.tiff` existiert, landet im Gams-Objekt als 
`foo.bar.1/img.tiff`, weil dort keine "Verzeichnisse" erlaubt sind.


TODO: Document relative URLs!

### Verpflichtende Datenströme

Der einzige verpflichtenden Datenstrom ist `DC.xml`.

## Nicht manuelle Erzeugung von Objektverzeichnissen

Die einfachste Form der Erstellung von Objektverzeichnissen ist, die Verzeichnisse
z.B. im Windows Explorer anzulegen und dann die Datenströme hineinzukopieren.

Natürlich lässt sich dieser Prozess auch automatisieren. `preprocess` bietet
hier zwei Werkzeuge:

  * [`preprocess gasm3export`](gams3export.md) exportiert Objekte aus 
    dem GAMS 3 Repository und legt diese als Objektverzeichnisse ab.
  * [`preprocess splitproject`](splitproject.md) nutzt Projektverzeichnisse, wie 
    sie typischerweise für den Ingest nach GAMS3 angelegt wurden als Ausgangsbasis
    und erzeugt daraus Objektverzeichnisse.
  * Projekte können natürlich auch eigene Script dazu entwickeln, etwa um Daten aus
    einer Tabellenform in ein Objektverzeichnis zu überführen.  

## Nächste Schritte

Nach dem Anlegen er Projektverzeichnisse sollte, falls noch nicht vorhanden, 
zunächste eine Projektkonfiguration erzeugt (`preprocess init`) und ergänzt werden. 
Dann kommt das [CSV Werkzeug](csv.md) zum Einsatz, das für jedes Objekt und jeden
Datenstrom Metadaten in csv Form erzeugt.