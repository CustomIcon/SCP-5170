(import logging)
(import asyncio)
(import sys)
(import time)
(import [.core.clients [client]])
(import [rich.logging [RichHandler]])
(import [pyromod [listen]])
(import [scp.utils.gitTools [getVersion]])


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
(setv bot (client "scp-bot"))
(setv user (client "scp-user"))
