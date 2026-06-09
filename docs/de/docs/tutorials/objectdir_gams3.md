# Objektverzeichnisse aus GAMS 3 exportieren


## Einzelne Objekte exportieren

Soll ein Projekt von Gams3 nach GAMS 5 migriert werden, sollte der Weg auch über Objektverzeichnisse
führen. Der Preprocess stellt dazu den Befehl 'gams3export` bereit. Dieses Tool
funktioniert so, dass man ein einzelnen Objekt über seinen PID angibt:

```
preprocess gams3export o:foo.bar.1
```

Dadurch werden alle Datenströme des Objekts `o:foo.bar.1` in ein neues Verzeichnis `objects/o%3Afoo.bar.1` gespeichert.

Will man das Präfix (hier: `o:`) verwerfen, kann man die Option `--strip-prefix` setzen:

```
preprocess gams3export --strip-prefix o:foo.bar.1
```

Das Objekt wir dann ins Verzeichnis `objects/foo.bar.1` geschrieben.

Standardmässig langen alle Objektordner in einem `objects` Verzeichnis direkt in dem Verzeichnis,
in dem man den Preprozessor aufruft. Mit der Option `--output-dir` (oder kurz: `-o`) kann man
ein anderes Verzeichnis angeben.

## Mehrere Objekte exportieren

In den meisten Fällen will man nicht einzelne Objekt exportieren, sondern z.B. alle Objekte eines
Projekts. Das geht einfach, indem man statt einer vollen Objekt-ID (PID) ein Muster mit Wirldcards
angibt. Es werden dann alle Objekte exportiert, für die dieses Muster passt.

```
preprocess gams3export '*:foo*'
```

Exportiert alle Objekte in deren PID die Zeichnkette `:foo` vorkommt. Wichtig dabei sind
die Anführungszeichen, damit die Wildcards nicht bereits von der Shell expandiert werden.

Alle Optionen funktionieren für den Export einzelner einzelner Objekte oder mehrerer Objekt.

Details zu den Optionen bekommt man entweder so:

```
preprocess gams3export --help
```

oder man liest in der [Befehlsreferenz](../reference/subcommands/gams3export.md) nach.