(import asyncio)
(require sys)
(import [pyrogram[idle]])
(import [scp[user bot]])
(import [scp.core.functions.plugins[loadPlugins]])
(import [scp.utils.selfInfo[updateInfo]])
(import [scp.utils.interpreter[shell]])
(import [scp.database.Operational[InitializeDatabase]])

;; (setv HELP_COMMANDS {})

(defn/a main []
    (await (bot.start))
    (await (user.start))
    (await (updateInfo))
    (await (InitializeDatabase))
    (await (
        asyncio.gather
            (asyncio.create_task
                (shell))
            (loadPlugins
                (.split
                    (user._config.get "scp-5170" "plugins")))
        )
    )
)


(if (= __name__ "__main__")
    (try
        (asyncio.run (main))
        (except [KeyboardInterrupt]
            (sys.exit 1))))
