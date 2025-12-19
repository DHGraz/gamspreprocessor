# Der Unterbefehl validate

Dieser Unterbefehl überprüft ein oder mehrere Objektverzeichnisse auf formale Korrektheit.
Da der Packager dieselbe Validierungsroutine verwendet, kann so bereits vor Verwendung des Packagers
sichergestellt werden, dass die Objektverzeichnisse korrekt angelegt wurden.

## Verwendung 

```
preprocess validate [OPTIONS] <VERZEICHNIS>
```

`VERZEICHNIS` ist hier der Pfad zu einem validierenden Objektverzeichnis oder einem 
Verzeichnis, das meherere Objektverzeichnisse enthält.

#### Optionen

####  `--continue-on-error`, `-c`

Normalerweise wird die Validierung nach dem ersten Validierungsfehler abgebrochen. Ist 
diese Option gesetzt, wird die Validierung für de restlichen Objektverzeichnisse fortgesetzt.

##### `--help`

Gibt den Hilfetext für diesen Unterbefehl aus.

