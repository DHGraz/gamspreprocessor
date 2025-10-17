# Der Unterbefehl project

Dieser Unterbefehl dient zum Anlegen von neuen Projekten und und zum Aktualisieren des Konfigurationsschemas.

## Verwendung 

```
preprocess project [OPTIONS] COMMAND [ARGS]...
```

## Unterbefehle

* `init` Erstellt eine grundlegende Projektstruktur und `project.toml`.
* `update` Bringt das Format der `project.toml` Datei auf den Stand der aktuellen Programmversion.

### init

Der Befehl `preprocess project init` erstellt eine grundlegende Verzeichnisstruktur für das Projekt und legt eine initiale  Konfigurationsdatei `project.toml` im Wurzelbverzeichnis des Projekts an. Diese Konfigurationsdatei muss danach händisch
an das jeweilige Projekt angepasst werden.

Beispiel:

```
preprocess project init [OPTIONS] projects/myproject
```

Mit diesem Befehl wird ein neues Projekt im Verzeichnis `projects/myproject` angelegt.


#### Optionen

##### `--help`

Gibt den Hilfetext für diesen Unterbefehl aus.


### update

`preprocess project update` aktualisiert das Format der Datei `project.toml`. 

```
preprocess project update [OPTIONS] CONFIG_FILE
```

Dieser Befehl sollte immer nach dem Upgrade auf eine neue Version das gamspreprocessors ausgeführt werden. Er sorgt dafür, dass das Format der bestehenden Konfigurationsdatei mit dem möglicherweise erweiterten neuen Format in der neuen Version abgeglichen wird.

#### Optionen: 

##### `--help`

Gibt den Hilfetext für diesen Unterbefehl aus.