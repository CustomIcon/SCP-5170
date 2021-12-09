(require configparser)
(import [scp[user]])


(defn/a checkTable [^str name]
    (try
        (setv tableID (user._config.getint ".internal" name))
        (except [configparser.NoOptionError]
            (setv table (await (user.send_message
                            :chat_id (user._config.getint ".internal" "databaseChannel")
                            :text "{}")))
            (user._config.set ".internal" name (str table.message_id))
             (with [file (open "config.ini" "w")]
                (user._config.write file))
            (setv tableID table.message_id)))
        (return tableID))
