(import logging)
(import hy) ; noqa
(import asyncio)
(import sys)
(import time)
(import [.core.clients [client]])
(import [rich.logging [RichHandler]])
(import [pyromod [listen]])
(import [scp.utils.gitTools [getVersion]])
(import pathlib)

(setv RUNTIME (time.time))
(setv Versions (getVersion))
(setv __longVersion__ (get Versions 0))
(setv __version__ (get Versions 1))
(logging.basicConfig
    :level logging.INFO
    :format "%(filename)s:%(lineno)s %(levelname)s: %(message)s"
    :datefmt "%m-%d %H:%M"
    :handlers [(RichHandler)]
)
(setv console (logging.StreamHandler))
(console.setLevel logging.ERROR)
(setv formatter (
    logging.Formatter "%(filename)s:%(lineno)s %(levelname)s: %(message)s")
)
(console.setFormatter formatter)
(setv cons (logging.getLogger ""))
(cons.addHandler console)

(setv log (logging.getLogger))
(setv loop (asyncio.get_event_loop))
(setv _path (pathlib.Path __file__))
(setv bot (client f"{(_path.parent.resolve)}-bot"))
(setv user (client f"{(_path.parent.resolve)}-user"))
