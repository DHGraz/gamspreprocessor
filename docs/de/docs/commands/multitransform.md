# multitransform

Anwendung von Transformationsszenarien auf mehrere Dateien.


`preprocess multitransform` funktioniert ähnlich wie `preprocess transform`, jedoch können mit `multitransform` Tranformationen 
auf mehrere oder viele Dateien und Objekte angewendet werden.

`preprocess multitransform` kann beispielsweise dafür verwendet werden, um mit einem Befehl für hunderte oder tausende 
Objektverzeichnisse aus dem in TEI-Files vorhandenen Metadaten `DC.xml` Dateien zu erzeugen.

Aktuell kann `multitransform` nur XSLT. Weitere Transformationen können aber bei Bedarf hinzugefügt werden.

## Verwendung 

```
preprocess multitransform [OPTIONS] COMMAND [ARGS]...
```

## Unterbefehle

* `preprocess multitransform saxon-version` Zeigt die Version des Saxon Prozessors an
* `preprocess multitransform xslt` Wendet eine xslt auf mehrere xml-Dateien an

### preprocessmultitransform xslt

`preprocess multitransform xslt` Wendet eine XSL Transformation rekursiv auf XML Dateien in mehreren Verzeichnissen an.
Funktioniert bei Bedarf auf rekursiv, das heißt, die Transformation kann auch auf Unterverzeichnisse angewendet werden.

Um festzulegen, welche Dateien transformiert werden sollen, gibt es zwei Wege:

  1. Eine Datei, die pro Zeile einen Pfad zu einer zu transformierenden Datei enthält.
     Diese Datei muss mit der Option `--file-list <PFAD ZUR DATEI>` bekannt gemacht werden.
     Wird dieser Weg verwendet, braucht kein Argument `START_DIR` angegeben zu werden 
     (dieses wird ignortiert), weil die zu transformierenden Dateien mit ihren Pfaden 
     ohnehin in der Datei aufgelistet sind.
  1. Durch Verwendung eines Dateinamenmusters via die Option `--pattern`. In diesem Fall muss mindestes 
     ein Ausgangspfad als Argument festgelegt werden. Das Programm such dann ausgehend von diesem
     Pfad nach Dateien, auf die das Muster passt, um die Transformation auf diese Dateien anzuwenden.

Es sollte klar sein, dass die beiden Optionen `--file-list` und `--pattern` nicht zusammen verwendet werden
dürfen.     


```
preprocess multitransform xslt [OPTIONS] [START_DIR]...
```

#### Optionen: 

##### --xslt-file <PFAD ZUR XSLT DATEI>, -x <PFAD ZUR XSLT DATEI>

Diese Option muss angegeben werden, weil über sie die zu verwendende XSLT Datei festgelegt wird.

##### --output-filename <NAME DER ZU ERZEUGENDEN DATEI>, -o <NAME DER ZU ERZEUGENDEN DATEI>

Diese Option muss angegeben werden. Achtung: Der Wert ist hier kein Pfad, sondern ein Dateiname. Eine entsprechende Datei 
wird in jedem Objektordner (konkret: im selben Ordner in dem die zu transformierende Datei liegt) erzeugt. Es wird also z.B.
in jedem Objektverzeichnis ein `DC.xml` erzeugt.

##### --pattern <TEXT>, -p <TEXT>

Der Wert dieser optionalen Option ist ein Dateinamen-Muster, über die festgelegt werden kann, welche Dateien
transformiert werden sollen. 
Ausgehen von mindestens einem Ausgangspfad, der über das Argument `START_DIR` festzulegen ist, sucht das Programm nun nach
Dateien, auf die das Muster passt und wendet die Transformation auf diese Dateien an.

Damit das Muster nicht bereits durch die Shell expandiert wird, empfiehlt es sich, das
Muster in Anführungszeichen zu setzen. 

Das Muster folgt der Pattern Language von `pathlib.glob`. Details dazu finden sich 
unter https://docs.python.org/3/library/pathlib.html#pathlib-pattern-language.


##### --recursive, -r

Ist diese Option gesetzt, wird rekursiv in Unterordnern nach Dateien gesucht, auf die das via `--pattern` festgelegt Muster passt.

Kann nur zusammen mit `--pattern` genutzt werden.
    
##### --exclude <DATEINAME>, -e <DATEINAME>

Über diese Option kann ein Dateiname angegeben werden, der bei der Transformation ignoriert werden soll.

Wenn als beispielsweise via via `--pattern '*.xml'`  festgelegt wird, dass alle XML Dateien transformiert werden sollen, 
führt ein `--exclude DC.xml` dazu, dass Dateien mit dem Namen `DC.xml` nicht transformiert werden.

Diese Option kann mehrfach verwendet werden werden. Beispiel: `--exclude DC.xml --exclude LIDO.xml`

Achtung: Der Wert dieser Option ist nur der Dateiname ohne Pfad.
    
##### --file-list <PFAD>, -l <PFAD>

Der Wert dieser Option ist der Pfad zu einer Datei, die wiederum Pfade zu Dateien enthält, die transformiert werden sollen (ein Pfad pro Zeile).

Der Gedanke hinter dieser Option ist, dass es manchmal einfacher ist, z.B. via `grep`, `find` oder mit einem selbst geschriebenen Script 
eine Liste von zu transformierenden Datei zu erzeugen, als dies über ein Muster festzulegen. Daher kann diese Option nicht zusammen mit
`--pattern` verwendet werden.


##### --help

Zeigt den Hilfetext für diesen Unterbefehl an.


### preprocess multitransform saxon-version

`preprocess multitransform saxon-version` Zeigt die Version des Saxon Prozessors an.

```
preprocess multitransform saxon-version [OPTIONS]
```

Zeigt die Version des installierten Saxon Prozessors an

#### Optionen: 

##### --help

Zeigt den Hilfetext für diesen Unterbefehl an.
