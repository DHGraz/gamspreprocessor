# PREPROCESSING AND PACKAGING

## Setup von Python und Virtual Environement

- Python 3.12.x aus dem Windows Store installieren
  Aktuell wird Version 3.12.x empfohlen
- in der Powershell die Python-Version prüfen: `python --version`
- Virtual environment anlegen: `python -m venv .venv`
- Virtual environment aktivieren: `.\.venv\Scripts\activate`


## gamspreprocessor und gamspackager installieren
- `pip install gamspreprocessor-x.y.z.tar.gz`
- `pip install gamspackaging-x.y.z.tar.gz`


## Verzeichnis für Projekt anlegen
- `mkdir <projektkuerzel>`
- `cd <projektkuerzel>`


## Projekt initialisieren
- `preprocess project init`
- legt an:
  - `project.toml`
  - `.gitignore`
  - `objects` Verzeichnis
- händisch lokal ein `bags` Verzeichnis anlegen

## `project.toml` bearbeiten
- Felder in der Sektion `[metadata]` korrekt ausfüllen

## `objects` Verzeichnis
- im Verzeichnis `objects` muss für jedes Digitale Objekt
  ein Unterorder angelegt werden, der als Namen den PID des
  Objekt hat!
- ins den jeweiligen Objektordner die TEIs und dazugehörige Dateien
  (z.B. Bilder usw.) ablegen


## Dublin Core
- `DC.xml` muss für jedes digitale Objekt erzeugt werden
  - für die TEI u. LIDO gibt's im `preprocessor` eine Pipeline,
    die mit Hilfe von XSLTs DC.xml für die Objekte erzeugt
  - `preprocess transform xslt -x <project.xsl> foo/TEI.xml foo/DC.xml`


## CSV bzw. Excel-Dateien erzeugen
- Felder in der CSV-Datei müssen überprüft u. evtl. korrigiert werden
- Windows-User sollten entweder einen einfachen Editor verwenden oder
  die CSV-Datei in Excel und zurück konvertieren. Dann nur die Excel-Datei
  bearbeiten
- Konvertierung von CSV nach Excel u. zurück wird noch überarbeitet
- Grundlegender Befehl: `preprocess csv create <root-folder>`


## Bags erzeugen
- sind alle obigen Anpassungen erfolgt, können Bags von den Objekten erzeugt werden
- `packager bag create <root-folder> -o <bag-folder>`
