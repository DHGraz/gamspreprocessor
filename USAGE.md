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
  - händisch lokal ein `bags` Verzeichnis anlegen
- Verzeichnisse:
```
<projektkuerzel>
├── bags
├─`─ objects
└─ project.toml
```

## `project.toml` bearbeiten
- nur die Felder in der Sektion `[metadata]` müssen korrekt ausgefüllt werden

## `objects` Verzeichnis
- im Verzeichnis `objects` muss für jedes Digitale Objekt
  ein Unterorder angelegt werden, der als Namen den PID des
  Objekt hat!
- in den jeweiligen Objektordner die TEIs und die dazugehörige Dateien
  (z.B. Bilder usw.) ablegen


## Dublin Core
- `DC.xml` muss für jedes digitale Objekt erzeugt werden
  - für die TEI u. LIDO gibt's im `preprocessor` eine Pipeline,
    die mit Hilfe von XSLTs jeweils ein DC.xml für die Objekte erzeugt
  - `preprocess transform xslt -x <project.xsl> foo/TEI.xml foo/DC.xml`
  - **NB**: Mindestens der Titel (`dc:title`) muss auf Englisch sein und 
    das Attribut `xml:lang="en"` enthalten


## CSV bzw. Excel-Dateien erzeugen
- Felder in der CSV-Datei müssen überprüft u. evtl. korrigiert werden
- Windows-User sollten entweder einen einfachen Editor verwenden oder
  die CSV-Datei in Excel und zurück konvertieren. Dann nur die Excel-Datei
  bearbeiten
- Konvertierung von CSV nach Excel u. zurück wird noch überarbeitet
- Grundlegender Befehl: `preprocess csv create <root-folder>`


## Bags erzeugen
- sind alle obigen Anpassungen erfolgt, können Bags von den Objekten erzeugt werden
- `packager bag create <root-folder|projektkuerzel> -o <bag-folder>`, z.B. Bags für das
  Projekt 'hsa': `packager bag create hsa -o bags`
