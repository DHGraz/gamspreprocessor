# project

Hilfsfunktionen um GAMS-Projekte zu managen. 

## Verwendung 

```
preprocess project [OPTIONS] COMMAND [ARGS]...
```

## Unterbefehle

* `preprocess project init` Erstellt eine grundlegende Projektstruktur und project.toml
* `preprocess project update` Updatet die project.toml Datei im aktuellen Ordner

### preprocess project init

`preprocess project init` Erstellt eine grundlegende Projektstruktur und project.toml

```
preprocess project init [OPTIONS] PROJECT_ROOT
```
* Erstellt eine grundlegende Projektstruktur und project.toml
* Optionen: 
    * --help 
        Zeigt Hilfe für diesen Befehl an

### preprocess project update

`preprocess project update` Updatet die project.toml Datei im aktuellen Ordner

```
preprocess project update [OPTIONS] CONFIG_FILE
```
* Dieser Befehl sollte ausgeführt werden, wenn sie das Schema in der Konfigurationsdatei geändert hat. Er kann so oft wie nötig ausgeführt werden, und überschreibt keine Einstellungen. Er fügt nur neue Einstellungen hinzu und entfernt alte. 
* Optionen: 
    * --help 
        Zeigt Hilfe für diesen Befehl an