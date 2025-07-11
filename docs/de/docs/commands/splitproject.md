###COMMENT: Hier sind ein paar Punkte bei deren Übersetzung ich mir nicht ganz sicher war###

# splitproject

Hilfsfunktionen um Objektordner anzulegen. Dieser Befehl ist nützlich, um einen GAMS3/4 Projektordner in mehrere Objektordner umzuwandeln, wie es für GAMS5 notwendig ist. ###COMMENT Nicht ganz sicher wie man "a GAMS3/4 style project directory" übersetzen kann###

## Verwendung 

```
preprocess splitproject [OPTIONS] COMMAND [ARGS]...
```

## Unterbefehle

* `preprocess splitproject showunhandled` Listet alle Dateien auf, die noch nicht einem Objekt zugeordnet sind.
* `preprocess splitproject split` Teilt Projektdateien in Objektordner auf

### preprocess splitproject showunhandled

`preprocess splitproject showunhandled` Listet alle Dateien auf, die noch nicht einem Objekt zugeordnet sind.

```
preprocess splitproject showunhandled [OPTIONS] OUTPUT_DIR
```
* Listet alle Dateien im Projektordner auf, die noch nicht mit einem split Befehl bearbeitet wurden.
* 'output-dir' ist das Wurzelverzeichnis der Objektverzeichnisse, das ist der Wert der bei '-o' ('--output-dir') im split Befehl gesetzt wurde. Falls kein Befehl gesetzt wurde, ist der Standard './objects'.
* Optionen: 
    * --help 
       Zeigt Hilfe für diesen Befehl an 

### preprocess splitproject split

`preprocess splitproject split` Teilt Projektdateien in Objektordner auf

```
preprocess splitproject split [OPTIONS] [SOURCEFILES]...
```
* Teilt projektdateien in Objektordner auf.
* Legacy Projekte bewahrten alle Objekte in einem einzigen Ordner auf. Dieser Befehl wird je einen neuen Ordner für jedes Objekt erstellen. ###COMMENT Bin mir nicht sicher, wie ich "legacy projects" übersetzen kann ###
* Die Argumente der Quelldateien akzeptieren eine Liste an Dateien zum Teilen. Falls die Shell Platzhalter unterstützt (die meisten tun dies), kann  man diese nutzen um die Dateien genauer anzugeben, z.B. 'somedir/*.xml' teilt alle xml-Dateien innerhalb des somedir Ordners. ###COMMENT: "Shell" beibehalten###
* Optionen: 
    * -o, --output-dir PATH
        Der ausgegebene Ordner, in dem die Objektordner erstellt werden. Standard: '<projectroot>/objects'
    * -f, --object-format [auto|tei|lido]
        Die Art der Dateien, die geteilt werden sollen. Standard ist 'auto'
    * -l, -file-list PATH
        Eine Datei, die eine Liste von Dateien, die geteilt werden sollen, entählt. Falls nötig mit Pfad.
    * -r, --replace
        Ersetzt existierende Objektordner. Nur verwenden, wenn nötig!
    * --reset
        Setzt den Bookkeeper zurück. Nur verwenden, wenn alles neu gemacht werden soll! ###COMMENT: Nicht sicher, wie man Bookkeeper übersetzt, beibehalten ###
    * --strip-prefix
        Der Präfix wird entfernt (z.B. o:)
    * --help
        Zeigt Hilfe für diesen Befehl an