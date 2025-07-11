# multitransform

Hilfsfunktionen um mehrere Dateien auf einmal umzuwandeln. Diese Funktion kann nützlich sein um GAMS-Dateien in andere Formate umzuwandeln. 

## Verwendung 

```
preprocess multitransform [OPTIONS] COMMAND [ARGS]...
```

## Unterbefehle

* `preprocess multitransform saxon-version` Zeigt die Version des Saxon Prozessors an
* `preprocess multitransform xslt` Wendet eine xslt auf mehrere xml-Dateien an


### preprocess multitransform saxon-version

`preprocess multitransform saxon-version` Zeigt die Version des Saxon Prozessors an.

```
preprocess multitransform saxon-version [OPTIONS]
```
* Zeigt die Version des Saxon Prozessors an
* Optionen: 
    * --help Zeigt Hilfe für diesen Befehl an

### preprocessmultitransform xslt

`preprocess multitransform xslt` Wendet eine xslt auf mehrere xml-Dateien an.

```
preprocess multitransform xslt [OPTIONS] [START_DIR]...
```
* Wendet eine xslt auf mehrere xml-Dateien an
* Optionen: 
    * -x, --xslt-file PATH
        [notwendig] Muss immer angegeben werden
    * -o, --output-filename TEXT
        [notwendig] Der Name der ausgegebenen Datei. Diese Datei wird im selben Ordner wie die Input-Datei erstellt. D.h., dass der Name der ausgegebenen Datei bei allen Umwandlungen gleich ist, aber in unterschiedlichen Ordnern
    * -p, --pattern TEXT
        Eine Struktur (*,?,!) um die Dateien zu identifizieren, die umgewandelt werden sollen. Kann nicht zusammen mit --file-list verwendet werden
    * -r, --recursive
        Wendet die Struktur, die als Argument festgelegt ist, auch in Unterordnern an. Kann nur zusammen mit --pattern genutzt werden
    * -e, --exclude TEXT
        Eine Liste der Dateinamen, die von der Umwandlung ausgeschlossen werden sollen. Dies ist eine List der Dateinamen (ohne Pfad!), keine Strukturen
    * -l, --file-list PATH
        Eine Datei, die eine Liste von Dateien enthält, die umgewandelt werden sollen (mit Pfad, falls nötig)
    * --help
        Zeigt Hilfe für diesen Befehl an