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

(setv RUNTIME (time.time)
    Versions (getVersion)
    __longVersion__ (get Versions 0)
    __version__ (get Versions 1)
    console (logging.StreamHandler))

(logging.basicConfig
    :level logging.INFO
    :format "%(filename)s:%(lineno)s %(levelname)s: %(message)s"
    :datefmt "%m-%d %H:%M"
    :handlers [(RichHandler)]
)
(console.setLevel logging.ERROR)
(console.setFormatter
    (logging.Formatter "%(filename)s:%(lineno)s %(levelname)s: %(message)s"))
(.addHandler (logging.getLogger "") console)

(setv log (logging.getLogger)
    loop (asyncio.get_event_loop)
    bot (client f"{(.parent.resolve (pathlib.Path __file__))}-bot")
    user (client f"{(.parent.resolve (pathlib.Path __file__))}-user"))
