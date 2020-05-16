# mport

#### Installation

```bash
python setup.py bdist_wheel
python -m pip install dist/mport-0.0.1-py3-none-any.whl
```

#### Usage

```bas
$ python -m mport -h
usage: Port mapping [-h] [-l LISTEN] -t TARGET [--timeout TIMEOUT] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  -l LISTEN, --listen LISTEN
                        Server listening address (default: localhost:11022)
  -t TARGET, --target TARGET
                        Target address (default: None)
  --timeout TIMEOUT     Port mapping timeout [second] (default: 30.0)
  --debug               Set logger level to debug (default: False)
```

+ create port mapping `localhost:11022` → `localhost:2022`

  ```bash
  $ python -m mport -t localhost:2022
  2020-05-16-14-37-01  INFO       MainProcess  root server listening at ('127.0.0.1', 11022)
  ```
