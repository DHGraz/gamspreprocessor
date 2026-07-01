# Tutorial zu split project

Existieren bereits Daten in einer Form wie sie bisher als Ausgangspunkt für den Ingest
via Cirilo genutzt wurden, können diese mit dem Unterbefehl `splitproject` in
Objektverzeichnisse konvertiert werden:

```
gamspreprocessor splitproject split /projects/foo/TEI_*.xml
```

Analysiert alle auf das angegebene Muster passende Dateien und erzeugt passende Objektverzeichnisse.


TODO: better example and explain what is done.

Details dazu finden sich in der [Referenz](../reference/subcommands/splitproject.md) zu diesem Befehl.
