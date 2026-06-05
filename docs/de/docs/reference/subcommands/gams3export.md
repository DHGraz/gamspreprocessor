# Der Unterbefehl gams3export

Der Unterbefehl `gams3export`dient dazu, ein oder mehrere in einem GAMS 3 
Repository abgelegt Objekte in einen oder mehrere Objektordner zu exportieren.

Dabei liegt der Fokus auf dem Export der Datenströme. Die so erzeugten 
Objektverzeichnisse können danach als Ausgangspunkt genommmen werden,
um die Daten in eine GAMS 5 kompatible Form gebracht zu werden. Typische
weitere Schritte sind etwa die Erzeugung einer Projektkonfiguration
(`gamsproject.toml`, die Überprüfung von DC.xml und die Erzeugung und Vervollständigung
von `object.csv` und `datastreams.csv`.

In der einfachsten Form kann der Subbefehl so verwendet werden:

```bash
prepocess gams3export 'o:foo.1'
```

Dieser Aufruf legt im Verzeichnis `objects` ein Verzeichnis `o%3Afoo.1` an. `%3A`
ist  einfach die URL-encodete Form eines Doppelpunkts. Dies ist nötig, 
weil Doppelpunkte nicht in jedem Dateisystem erlaubt sind. In diesem 
Verzeichnis wird für jeden Datenstrom
eine entsprechende Datei angelegt. Da Datenströme in GAMS 3 keine 
Dateinamenerweitung tragen, wird diese aus dem MIME-Type des Datenstroms 
abgeleitet. Manche Datenströme (z.B. `QR`) werden ignoriert, manche
Datenströme (wie z.B. METHODS) werden zwar exportiert, landen aber
in einem speziellen Ordner `.special_datastreams`, der vom Packager
ignoriert wird. Dort landen auch zwei Datenströme, die von GAMS 3 
nicht direkt bereit gestellt werden: `audit_trail.json`
und `objectproperties.json`. 
 

Es können auch mehrere Objekte(z.B. alle Objekte eines Projekts) 
mit einem Aufruf exportiert werden, indem ein PID-Muster angegeben wird:

```bash
preprocess gams3export '*foo*'
```

## Verwendung

```
preprocess gams3export [OPTIONS] PID-PATTERN
```

### Optionen 

Das Verhalten von `splitproject` kann über folgende Optionen beeinflusst werden:

#### `--output-dir, -o`

Mit dieser Option kann ein Pfad zu einem Ordner angegeben werden, in dem 
die zu exportierenden Objektordner angelegt werden. Wird diese Option nicht
gesetzt, landen die Objekte im Ordner `objects`, direkt unter dem Verzeichnis,
aus dem das Programm gestartet wurde. Das jeweilige Verzeichnus MUSS bereits
existieren.

#### `--replace, -r`

Stößt der Exporter auf ein bereits existierendes Objektverzeichnis, wird
der Export für dieses Objekt normerweise übersprungen. Das ist nützlich, weil so
die Objektverzeichnisse in mehreren Durchläufen ergänzt werden können ohne 
immer alles neu zu exportieren.

Falls aber bestehende Objekte neu exportiert werden sollen, 
kann die Optione `--replace` (Kurzform: `-r`) gesetzt werden.


#### `--strip-prefix`

Ab GAMS Version 5 wird empfohlen, keine Typ-Prefixe wie `o:` oder `context:` mehr
zu verwenden. Ist die Option `--strip-prefix` gesetzt, wird das Prefix vor dem
Erzeugen des Objektnamens abgestreift. 

Es muss von Fall zu Fall entschieden werden, ob beim Übertragen eines Projekts 
von GAMS 3 nach GAMS 5 Präfixe beibehalten werden sollen oder nicht.

#### `--base-url` 

Standardmässig holt `gams3export` die Objekte von `https://gams.uni-graz.at/archive`.
Soll von einer anderen Repository-Instanz exportiert werden, so kann diese als Wert
dieser Option angegeben werden. Dabei ist zu beachten, dass nicht nur der Name des
Servers anzugeben ist, sondern auch der Basispfad zum Repository am Server.

#### `--colon-replacement`

Über diese Option kann festgelegt werden, dass Doppelpunkte in
Objekt-Verzeichnisnamen nicht durch `%3A` sondern durch ein (oder mehrere)
alternative Zeichen ersetzt werden.

Diese Option ist nur für sehr spezielle Use Cases gedacht. 
**Sie sollte im Normalfall NIE verwendet werden, da der Packager den
Defaultwert `%3A` erwartet.**


#### `--help`

Gibt den Hilfetext zum Subbefehl aus.