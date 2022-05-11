# text-checker

Text checker using Reverso

## Installation 

### (Optional) Virtual environment

We recommend using a python virtual environment :

```bash
virtualenv venv
source venv/bin/activate
```

### Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Help on usage

```bash
python3 -m textchecker -h
```

### Spell-check a text in a file

```bash
python3 -m textchecker path/to/file.txt
```

### Example

Input:

```
Voici une texte avec quelque fautes.
Il peu etre long ou non. Ceci est un example.
```

Output:

```bash
Loading corrections...
 ████████████████████████████████████████████████████████████  100%
Voici une texte[un texte] avec quelque[quelques] fautes.
Il peu[peut] etre[être] long ou non. Ceci est un example[exemple].
```
