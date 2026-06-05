# Installation

`gamspreprocess` steht als Package auf pypi.org zur Verfügung. 
Nach der Installation (z.B. via `uv` oder `pip`) steht das `preprocess`
Programm zur Verfügung.

## Normale Verwendung

Soll `preprocess` zur normalen Verwendung installiert werden, empfehlen wird diesen Weg:

### Voraussetzung: Installation von `uv`. 

`uv` ist ein alternativer Paketmanager, der das Leben mit Python erheblich erleichtert. Allerdings muss uv
zuerst installiert werden. 

#### Installation unter Windows

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Installation unter macOS und Linux

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Installation mit pip

Grundsätzlich kann `uv`auch mit pip installiert werden, steht aber dann je nach aktivem Environment nur in diesem zur Verfügung:

```
pip install uv
```

### Temporäre Installation von ```gamspreprocess```

Ist `uv` installiert, kann `gamspreprocessor so ausprobiert werden:

```
uvx gamspreprocessor preprocess
```

### Dauerhafte Installation von `gamspreprocessor`
```
uv tool install gamspreprocessor
```

Danach steht das Programm `preprocess` direkt zur Verfügung

### Installation ohne uv

Falls auch welchen Gründen auch immer `uv` nicht installiert werden kann, kann `gamspreprocessor` auch ganz
normal mit `pip` installiert werden:

```
pip install gamspreprocessor
```

Danach muss aber immer zuerst das virtuelle Environment aktiviert werden, in dem `ganspreprocessor` installiert worden ist.


## Installation für Development

Soll weiter an gamspreprocessor gearbeitet werden, lässt sich eine dafür geeignete Umgebung mit wenigen Schritten
herstellen:

1. `git clone https://zimlab.uni-graz.at/gams5/production/preprocessing/gamspreprocessor.git`
2. cd gamspreprocessor
3. uv sync


Bitte beachten Sie, dass die eigentliche Entwicklung auf einer privaten GitLab Instanz stattfindet. Es gibt zwar einen Mirror 
auf Github, dieser akzeptiert aber keine Pull-Requests.