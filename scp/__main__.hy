(import asyncio)
(import [pyrogram[idle]])
(import [scp[user bot]])
(import [scp.core.functions.plugins[loadBotPlugins loadUserPlugins loadPrivatePlugins]])
(import [scp.utils.selfInfo[updateInfo]])
(import [scp.utils.interpreter[shell]])
(import [scp.database.Operational[InitializeDatabase]])

(setv HELP_COMMANDS {})
(setv loop (asyncio.get_event_loop))

(defn/a main []
    (await (bot.start))
    (await (user.start))
    (await (updateInfo))
    (await (InitializeDatabase))
    (await (
        asyncio.gather
            (asyncio.create_task
                (shell))
            (loadBotPlugins)
            (loadUserPlugins)
            (loadPrivatePlugins)
        )
    )
)

(loop.run_until_complete (main))
