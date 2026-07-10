# object.csv

Die Datei `object.csv` enthält zusätzliche Metadaten über ein digitales Objekt.

## Die Spalten von `object.csv`

Die Datei besteht aus folgenden Spalten:


| Key          | Required  | Beschreibung                               | Beispiel       |  
| ----------   | --------- | ------------------------------------------ | -------------- |
| recid        | true      | PID des dig. Objekts                       | detamax.diary |   
| title        | true      | Titel des dig. Objekts                     | Detamax Diary |     
| project      | true      | Projektkürzel                              | detamax       |   
| description  | false     | Beschreibung des dig. Objects              | Diary of Detamax    | 
| creator      | true      | Creator des dig. Objekts                   | Max Musterfrau  | 
| rights       | true      | Lizenz: Name (URI)                         | Public Domain (http://creativecommons.org/publicdomain/mark/1.0/)| 
| publisher    | true      | Publisher of object                        | GAMS | 
| source       | true      | Quelle aus der dig. Objekt generiert wurde | local |                 
| objectType   | true      | basierend auf dc:type                      | text |
| mainResource | false     | PID des Hauptdatenstroms                   | TEI.xml |
| funder       | true      | Fördergeber                                | FFW (ausschreiben?) |
| tags         | false     | Frei zu vergebende Tags                    |Tag1; Tag2 |


### recid

`recid` ist der Identifikator des digitalen Objekts. Also etwas wie `hsa.letters.123`.

Bei der Generierung des CSV (`gamspreprocessor csv create`) wird der Ordnername des Objekts als Defaultwert
eingetragen.

### title

`title` ist der Titel des digitalen Objekts. Er wird aus DC.xml extrahiert. Fehlt der Wert
im DC.xml, wird der Name des Objekts (`recid`) verwendet.


### project

`project` bezeichnet das Projektkürzel. Jedes digitale Objekt muss initial einem Projekt zugeordnet werden.
Ist der Wert von `project_id` in `project.toml` gesetzt, wird dieser Wert verwendet.


### description

`description` ist die verbale Beschreibung des Objekts. Dieser Wert ist optional.


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

### source

`source` beschreibt die Herkunft der Daten. Er wird auf den Defaultwert `local` gesetzt und sollte gegebenfalls in der CSV-Datei geändert werden.

### objectType

Dieser Wert beschreibt die Art des Objekts, wie im DCMI Type Vocabulary festgelegt (https://www.dublincore.org/specifications/dublin-core/dcmi-type-vocabulary/). Der Default Type ist `text`.


### publisher

`publisher` legt fest, wer das Objekt publiziert hat. Standardmässig wird hier 'GAMS' verwendet.

### mainResource

`mainResource` erwartet als Wert die ID (`dsid`) des "Hauptdatenstroms" des Objekts. Dies ist der Datenstrom, der bei Aufruf des Objekts angezeigt wird.
Falls es keinen Hauptdatenstrom gibt, kann der Wert leer bleiben.

### funder

`funder` beschreibt, wer die Erstellung des Objekts finanziert hat. Ist in `project.toml` ein entsprechender Eintrag `metadata.funder` vorhanden, wird dieser verwendet.

### tags

Frei zu vergebende Tags. Mehrere Tags können durch `;` (Semicolons) getrennt angegeben werden. Das `tags` Feld kann leer bleiben, wenn es nicht benötigt wird.

Dieses Feld bietet die Möglichkeit, zusätzliche Filtermöglichkeiten zu realisieren, die sinnvollerweise nicht über die normalen Metadaten möglich oder sinnvoll sind.

Hinweis: Falls gewünscht kann beim `csv create` Unterbefehl durch Setzen der Option `--use-subjects-as-tags` dieses Feld mit allen in DC.xml vergebenen 
Werten von `dc:subject` vorbelegt werden.

## Beispiel

TODO