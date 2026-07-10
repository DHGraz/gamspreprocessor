## project.toml

Die Datei `project.toml` enthält die Konfigurationseinstellungen für die `gams-xxx` 
Programme, speziell für das Preprocessing Werkzeug.

Im Prinzip ist es es egal, wo diese Datei liegt, wir empfehlen aber das 
Wurzelverzeichnis des Projektordners. Idealerweise sollte es nur eine
einzige Konfigurationsdatei pro Projekt geben. Die einzelnen Settings
können bei Bedarf, wie weiter unten über Umgebungsvariablen bzw. 
ein `.env` File adaptiert werden.


### Erzeugung einer basalen Konfiguration

Der Befehl 

```
preprocess project init <project-root>
```

erzeugt im Verzeichnis `<project-root>' unter anderem eine `project.toml`
Datei. Diese muss danach mit einem Texteditor an das aktuelle Projekt
angepasst werden.

Da in Zukunft möglicherweise Erweiterungen des Formats von `project.toml` 
nötig werden, gibt es einen weiteren Befehl, mit dem eine existierende
Konfiguration angepasst werden kann:

```
preprocess project update
```

### Aufbau

`project.toml` besteht aus zwei Asbchnitten (in TOML Speak 'Tables'):

   * metadata
   * general

#### Konfigurationsoptionen im Abschnitt metadata   

##### project_id

`project_id` legt die Sigle des Projekt fest. z.B: `hsa`.
Dieser Wert wird bei der Erzeugung der csv-Dateien verwendet.

##### creator

Dieser Wert bezeichnet die Person oder Institution, die für die 
Erstellung des **digitalen** Objekts verantwortlich war.

Dieser Wert wird für die Erstellung der CSV-Dateien verwendet. Wenn die einzelnen
Objekte eines Projekts untschiedliche Creators haben, empfiehlt es sich u.U. diesen
Wert leer zu lassen und die `creator` Werte händisch in das Excel File einzutragen.
Eine weitere Möglichkeit wäre, die CSV-Dateien der von unterschiedlichen Creators 
erzeugten Objekte (z.B. verzeichnisweise) zu generieren und den jeweiligen 
Creator-Wert per Umgebungsvariable zu setzen.

##### funder

Funder ist der Name der die Erstellung des digitalen Objekt finanzierenden
Einrichtung. 

##### publisher

Dieser Werte sollte im Normal auf `GAMS` belassen werden, wenn das Objekt
in der GAMS publiziert wird.

##### rights 

`rights`spezifiziert die Lizenz unter der das digitale Objekt
publiziert wird. Defaultwert ist
`Creative Commons Attribution-NonCommercial 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)`

Andere Lizenzen sollten nach Möglichkeit diesem Muster folgen: `Name der Lizenz (URI)`, also z.B.:
`Public Domain (http://creativecommons.org/publicdomain/mark/1.0/)`.



#### Konfigurationsoptionen im Abschnitt general   

##### dsid_keep_extension = true

Normalerweise wird bei der Erzeugung von Datenstrom-Ids die 
Dateinamenerweiterung der Datenstrom-Datei beibehalten. Soll 
diese (wie in der alten GAMS) abgestreift werden, muss dieser Wert 
auf `false` gesetzt werden.

##### loglevel = "info"
Dieser Wert legt die "Gesprächigkeit" des Logging fest.
Defaultwert ist `info`. Andere mögliche Werte sind
`debug`, `warning`, `error` oder `critical`.

##### format_detector = "magika"

Für diverse Aufgaben muss das Format von Datenstromdateien ermittelt werden.
Wir bieten dazu den Möglichkeit, den dazu verwendeten "Detector" in der
Konfiguration festzulegen. Aktuell sind folgende Detektoren implementiert:

  - base - Ein sehr simpler Detector basierend auf dem mimetypes Modul. 
    Diese Detektor erschließt den Typ der Datei mehr oder minder aus der
    Dateinamenswerweiterung.
  - magika  - Dieser Detektor nutzt im Hintegrund die `magika` Bibliothek
    von google, die mehrere hundert Formate KI-basiert erkennt. Aktuell
    ist dieser Dedektor voreingestellt.

In Zukunft wird es noch mindestens einen weiteren Detektor geben, der über das
Netzwerk angesprochen werden kann und eine Software nutzt, dass im Bereich
der Langzeitarchivierung von Daten erprobt ist.

# If you want to use a detector service like a FITS Server, set this to the URL
# No supported, yet
##### format_detector_url = ""

Dieser aktuell noch ungenutzte Wert, ermöglicht, die URI festzulgeben, über
die eine netzwerkbasierte Formaterkennung angesprochen werden kann.


#### Beispiel


```toml

# [metadata] contains general metadata for the GAMS project
[metadata]
# the id of the project (eg.: hsa)
project_id = ""  

# The project creator (like in Dublin Core)
creator = "" 

# Set this to the funder of the project. Will be added to each object metadata
funder = ""

# You might want to keep this value ("GAMS")
publisher = "GAMS"  

# Set the default license for the project. 
# Can be overriden in project.csv and datastream.csv for single objects/data streams
rights = "Creative Commons Attribution-NonCommercial 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)"



[general]
# Normally dsid is the full filename (with extension). Set to false to strip extension for dsid.
dsid_keep_extension = true

# debug, info, warning, error or critical
loglevel = "info"

# magika, base (pythons built in mimetypes) 
# Default is magika
format_detector = ""

# If you want to use a detector service like a FITS Server, set this to the URL
# No supported, yet
format_detector_url = ""
```

### Setzen von einzelnen Konfigurationswerten 

Manchmal kann es nützlich sein, eine gemeinsame Konfigurationsdatei zu
nutzen, jedoch einzelne Konfigurationswerte auf dem jeweiligen Rechner 
(oder für spezielle Verzeichnisse) zu ersetzen. Ein Szenario dafür wäre
etwa, wenn es unterschiedliche 'creator' Werte gibt. 

Dazu werden zwei Mechanismen unterstützt: 1) Die zu ersetzenden Werte via
Umgebungsvariable zu setzen oder 2) im aktuellen Arbeitsverzeichnis eine
Datei `.env` anzulegen, die die zu ersetzenden Werte enthält. Man könnte
sogar beides gleichzeitig nutzen, wobei die Werte in dieser Reihenfolge 
gelten:

   1. Ist der Wert als Umgebungsvariable gesetzt, wird dieser verwendet
   2. Ist ein Wert nicht als Umgebungsvariable gesetzt, aber in `.env`,
      wird dieser Wert verwendet.
   3. Ist ein Wert weder als Umgebungsvariable gesetzt, noch via `.env`,
      so wird der Wert von `project.toml` verwendet.
   4. Ist der Wert auch hier nicht gesetzt, wird bei manchen Werten
      ein Defaultwert verwendet. Welche diese sind, ist oben bei der
      Beschreibung der Konfigurationswert vermerkt.

#### Konfigurationwerte über Umgebungsvariablen setzen

Die einzelnen Werte aus `project.toml` können mit einem davor
gestellten `GAMSCFG_` und dem durch ein weiteres `_` getrennten
Abschnittsnamen als Umgebungsvariable gesetzt werden. Um also
beispielsweise einen anderen `creator` im Abschnitt `metadata`
über eine Umgebungsvariable zu setzen:

```sh
export GAMSCFG_METADATA_CREATOR="John Doe"
```

bzw. in einer Windows-Shell

```
set GAMSCFG_METADATA_CREATOR="John Doe"
```

#### Konfigurationswerte über eine .env Datei setzen

Sollen die Konfigurationswerte abhängig von einem bestimmten Verzeichnis 
verändert werden, kann man in diesem Verzeichnis eine `.env` Datei
anlegen und die zu verändernden Werte dort setzen.  Der Name des neu
zu setzenden Wertes setzt sich zusammen aus dem Abschnittsnamen und, getrennt
durch einen Punkt, dem Namen des Konfigurationswertes:

```
metadata.creator = "John Doe"
general.format_detector = "base"
```

**Achtung:** Die `.env` Datei muss in dem Verzeichnis liegen, in dem das Script
ausgeführt wird (und nicht etwa in den Verzeichnis wo die Daten liegen)!

