(import configparser)
(import [scp [user]])


(defn/a InitializeDatabase[]
    (try
        (user._config.getint ".internal" "databaseChannel")
        (except [configparser.NoSectionError]
            (with [file (open "config.ini" "w")]
                (user._config.add_section ".internal")
                (setv channel
                    (await (user.create_channel "scp-Database"
                            :description "Do not Play with this channel!")))
                (user._config.set
                    ".internal" "databaseChannel" (str channel.id))
                (user._config.write file)))))
