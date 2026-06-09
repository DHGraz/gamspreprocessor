# datastreams.csv

Die Datei `datastreams.csv` enthält zusätzliche Metadaten über die Datenströme (Dateien) eines digitalen Objekts.

## Die Spalten von `datastreams.csv`


Die Datei besteht aus folgenden Spalten:

| Key          | Required  |  Beschreibung                               |  Beispiel |  
|------------- | --------- |  ------------------------------------------ |  --------- |
| dspath       | true      |  Pfad zur Datei (Verzeichnisnae/Dateiname)  |  detamax.diary/DC.xml |
| dsid         | true      |  Name des Datenstrims                       |  DC.xml |
| mimetype     | true      |  Content Type des Datastreams               |  image/jpeg |
| title        | false?    |  Titel des Datenstroms                      |  Dublin Core Metadata |
| description  | false     |  Beschreibung des Datenstroms               |  Portrait of M. Mustermann, ca. 1906 |
| creator      | true      |  Creator des Datenstroms                    |  Max Musterfrau |
| rights       | true?     |  Lizenz des Datenstroms: Name (URI)         |  Public Domain (http://creativecommons.org/publicdomain/mark/1.0/) |
| lang         | false     |  Sprache(n) des Datenstroms                 |  de; en  |
| tags         | false     |  Frei zu vergebende Tags                    |  foo; bar |

### dspath

`dspath` bezeichnet den zweiteiligen (Objektverzeichnis/Dateiname) Pfad zur in das Bag aufzunehmende Datei.
Der erste Teil ist also kein vollständiger Pfad, sondern nur die Objektid, also der Wert, der in object.csv als `recid` vergeben wurde. 
Ein Beispiel könnte also so aussehen: `hsa/TEI.xml`. Der Wert wird automatisch gesetzt und braucht im Normallfall nie verändert zu werden.

### dsid

Das ist der (finale) Name des Datenstroms. Dieser kann sich vom Dateinamen unterschieden, sollte aber der Übersichtlichkeit halber gleich sein. Der Name wird im Zuge der Generierung der CSV-Datei automatisch aus dem Dateinamen abgeleitet. Abhängig davon, ob in `project.toml` der Wert von `general.dsid_keep_extension`auf `true`(default) oder `false` steht, wird die Dateinamenerweiterung entweder erhalten oder abgestreift. 

### mimetype

Beschreibt den Content Type des Datenstroms. Diesen explizit zu setzen, solle fast nie nötig sein, weil
er für viele Formate automatisch ermittelt werden kann. 

### title

Ein Titel für den Datenstrom wird nur für einige wenige Dateinamen automatisch gesetzt:

Für einige wenige Dateinamen haben wir eigene Defaultwerte definiert:

  * `DC.xml`: "Dublin Core Metadata"
  * `RDF.xml: "RDF Statement"

Für alle anderen Datenströme bleibt das Feld beim automatischen Generieren der CSV Datei leer.


### description

`description` ist die verbale Beschreibung des Inhalts der Datenstroms. Dieser Wert ist optional.
Automatisch befüllt wird dieses Feld nur für 'DC.xml': 
"Dublin Core meta data in XML format for this Object"


### creator

`creator` ist der Name der Person, die das digitale Objekt erzeugt hat. Ist der Wert von `metadata.creator` in `project.toml` gesetzt, wird dieser Wert verwendet.

### rights

Dieses Feld beschreibt die Nutzungsbedingungen (Lizenz) für das Objekt. Idealerweise sollte dies
der ausgeschriebene Name der Lizenz sein, gefolgt vom der URI zur Lizenz in runden Klammern:

```
Creative Commons Attribution-NonCommercial 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)
```

Dieser Wert wird automatisch in dieser Reihenfolge ermittelt:

  1. Aus dem Dublin Core
  2. Aus `project.toml`: `metadata.rights`
  3. Der Defaultwert ( `Creative Commons Attribution-NonCommercial 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)`)


### lang

`lang` bezeichnet den oder die Sprache(n) des Datenstroms. Empfohlenes Format ist IETF BCP 47 
(https://www.rfc-editor.org/info/bcp47). Alternativ können ISO 639 Codes verwendet werden.

Mehrere Sprachen können durch ein Semikolon getrennt werden.

### tags

Tags sind frei wählbare Bezeichner. Das Feld ist optional. Mehrere Werte werden durch Semikolons (`;`) voneinander getrennt.





## Beispiel

TODO