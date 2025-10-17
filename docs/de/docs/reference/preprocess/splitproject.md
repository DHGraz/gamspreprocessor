# splitproject

Der Unterbefehl `splitproject` ist dazu gedacht, aus bestehenden GAMS 3 Projektdaten Objektordner für GAMS 5 zu erzeugen. Der Befehl ist also nur für Mitarbeiter:innen des DDH relevant.

Sie benötigen diesen Unterbefehl also nur, wenn Sie alte Projekte direkt von den Ausgangsdaten (wie sie im `projects`Ordner liegen) aus in Objektordner umwandeln wollen.


## Verwendung 

```
preprocess splitproject [OPTIONS] COMMAND [ARGS]...
```

## Unterbefehle

* `showunhandled` Listet alle Dateien auf, die noch keinem Objekt zugeordnet wurden.
* `split` Teilt Projektdateien in Objektordner auf


### split

Dieser Unterbefehl teilt Projektdateien in einzelne Objektordner auf.

```
preprocess splitproject split [OPTIONS] [SOURCEFILES]...
```

Alte Projekte bewahrten meist alle zu ingestierenden Objekte in einem einzigen gemeinsamen Ordner auf. 

Dieser Befehl trennt die Dateien in diesem gemeinsamen Ordner in ein Verzeichnis pro Objekt auf.

Als Argumente erwartet der Subbefehl eine Liste von Dateien, die Objektverzeichnissen zugeordnet werden sollen.
Falls die verwendete Shell Platzhalter unterstützt (die meisten tun dies), kann  man diese nutzen um die 
Dateien über ein Muster anzugeben, z.B. 'somedir/*.xml' teilt alle xml-Dateien innerhalb des somedir Ordners. 

#### Optionen: 

##### `--output-dir PATH`, `-o <PATH>`

Pfad zu einem  Ordner, in dem die Objektordner erstellt werden sollen. 
Standardwert ist  `<projectroot>/objects`

##### `--object-format [auto|tei|lido]`, `-f [auto|tei|lido]

Die Art der Dateien, die geteilt werden sollen. Standard ist 'auto'.

##### `--file-list <PFAD>`, `-l <PFAD>`

Eine Datei, die eine Liste von Dateien, die geteilt werden sollen, enthält. 

##### `--replace`, `-r`

Ersetzt existierende Objektordner. Diese Option ist gefährlich, weil damit unbeabsichtigt bereits bearbeitete Objekt 
erzetzt werden können. Also nur verwenden, wenn Sie sicher sind, dass bestehende Objektordner wirklich gelöscht und neu
angelegt werden sollen.

##### `--reset`

Setzt die "Buchhaltung" über bereits bearbeitet Dateien/Objekte zurück.
Diese Option darf nur verwendet werden, wenn alle bereits geleistete Arbeit verworfen werden soll.
Diese Aktion ist irreversibel, also Achtung!

##### `--strip-prefix`

Wird diese Option gesetzt, wird beim Splitten das Präfix aus der Objekt-ID (PID) entfernt, das in der neuen GAMS keine Rolle mehr spielt. Aus `o:foo.1` wird also `foo.1`, wenn diese Option gesetzt ist.


##### `--help`

Zeigt den Hilfetext für diesen Unterbefehl an.


### showunhandled

`preprocess split showunhandled` listet alle Dateien auf, die noch nicht einem Objekt zugeordnet sind, d.h. die noch nicht in einen Projektordner kopert worden sind. Dieser Befehl dient der Kontroll, ob alle vorhandenen Dateien umgewandelt worden sind.

```
preprocess splitproject showunhandled [OPTIONS] OUTPUT_DIR
```

Listet alle Dateien im Projektordner auf, die noch nicht mit einem split Befehl bearbeitet wurden.

`output-dir` ist das Wurzelverzeichnis der Objektverzeichnisse.
Da ist derselbe Pfad, der beim Unterbefehl `split` als Wert der Options `--output-dir` gesetzt wurde. 
Standardmässig wird  `./objects` verwendet.

#### Optionen: 

#####  `--help`
       
Zeigt Hilfe für diesen Unterbefehl an.