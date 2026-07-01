# Basics: Objektverzeichnisse

Im gamspreprocessoring von GAMS Daten sind **Objekverzeichnisse** zentral.

Die Grundidee ist, dass jedes Objekt in einem eigenen Verzeichnis angelegt wird:

   * Der Verzeichnisname MUSS die Objekt-ID sein (PID). Für GAMS 5 Objekte
     sollte kein Prefix (wie o: oder context:) mehr verwendet werden, grundsätzlich
     ist es aber weiterhin möglich diese zu verwenden. In diesem Fall MUSS aber
     der Doppelpunkt url-encoded, also durch `%3A` ersetzt werden. Die Daten eines
     Objekts mit der PID `o:foo.bar.1` müssen also in einem Verzeichnis mit dem Namen
     `o%3Afoo.bar.1` liegen.
   * Die einzige  Vorgabe eines Objektverzeichnisses ist, dass eine 
     Datei  `DC.xml` mit den Dublin Core Metadaten existieren muss.
   * Jede Datei im Objektverzeichnis repräsentiert einen Datenstrom. Die 
     Dateinamenerweiterung  (z.B. `.xml`) bleibt im Normalfall erhalten.
     Es gibt aber die (nicht empfohlene) Möglichkeit, die Erweiterung beim
     Paketieren später abzustreifen.
   * Der Packager erwartet zwei zusätzliche Dateien, die allerdings nicht in
     der Gams landen: `object.csv` und `datastreams.csv`. Diese können weitgehend
     automatisiert erzeugt werden. Dieser Vorgang ist in einem eigenen 
     Tutorial beschrieben.

## Erzeugung von Objektverzeichnissen

Es gibt mehrere Wege, die benötigten Objektverzeichnisse zu erstellen. Diese werden
im Detail in eigenen Tutorials beschrieben. Daher hier nur ein Überblick:

  * Händisch: Das ist vermutlich die umständlichste Art aber vermutlich bei neuen 
    Projekten durchführbar.
  * Durch eigene Scripte. Hier stehen natürlich alle Möglichkeiten offen, etwa ein 
    Excel-artiges  Sheet als Ausgangspunkt zu verwenden.
  * Objekte aus GAMS Version 3 in Objektverzeichnisse exportieren. Für diesen Zweck stellt
    der gamspreprocessor einen eigenen Unterbefehl zur Verfügung: 
    [`gamspreprocessor gams3export`](objectdir_gams3.md).
  * Objektverzeichnisse aus Daten erzeugen, wie sie typischerweise für den Ingest
    in GAMS 3 angelegt wurden. Der gamspreprocessor stellt dafür einen Unterbefehl
    [`gamspreprocessor splitproject`](objectdir_splitproject.md) bereit.    


## Datenströme

Die Datenströme eines Objekt werden im Objektverzeichnis als Dateien abgelegt. 
Der Dateiname entspricht dabei der Datenstrom ID. Groß- und Kleinschreibung wird übernommen.

Datenströme in Unterverzeichnissen des Objektordners sind zwar grundsätzlich möglich, 
werden aber beim Erzeugen des SIP eliminiert. Ein Datenstrom der im Objektverzeichnis als
`foo.bar.1/images/img1.tiff` existiert, landet im Gams-Objekt als 
`foo.bar.1/img.tiff`, weil dort keine "Verzeichnisse" erlaubt sind.


### Referenzen in Datenströmen

Um eine möglichst große Portabilität der Daten zu garantieren, sollten Referenzen 
nach Möglichkeit immer relativ (zum Objektordner) angegeben werden. 

Beispiel: wir in einem TEI ein Bild im selben Objekt referenziert kann man
einfach `="img1.jpg"` oder `="./img1.jpg"` angeben. Im Packager werden Referenzen 
NICHT mehr automatisch umgeschrieben, sie müssen also bereits im Objekverzeichnis korrekt
sein und funktionieren!

### Verpflichtende Datenströme

Der einzige verpflichtenden Datenstrom ist `DC.xml`.    