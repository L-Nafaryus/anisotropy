# anisotrope-cube

## Requirements
* python 3.5>
* OpenFOAM
* SALOME
* ParaView

## Getting started

* Clone project:
```bash
$ git clone git@github.com:L-Nafaryus/anisotrope-cube.git
$ cd anisotrope-cube
```

* Run single structure via SALOME GUI:
```bash
$ salome

python> exec(open("PATH/simpleCubic.py").read("rb"), args=("", 0.1, "001"))
```
where `PATH` is a full path to `anisotrope-cube/src/`.

* Generate all structures with configured parameters:
```bash
$ python src/genmesh.py
```

* All meshes + calculations:
```bash
$ ./build.sh
``` 
