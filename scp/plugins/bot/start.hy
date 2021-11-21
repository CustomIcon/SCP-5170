(import [scp[bot user __version__ __longVersion__]])
(import [scp.utils.selfInfo[info]])


(with-decorator (
    bot.on_message :filters (bot.command "start" :prefixes "/"))
    (defn/a _ [_ message]
        (setv text
            (user.md.KanTeXDocument
                (user.md.Section "SCP-5170"
                    (user.md.KeyValueItem
                        (user.md.Bold "Userbot Status")
                            (user.md.Code "Running"))
                    (user.md.KeyValueItem
                        (user.md.Bold "Version")
                            (user.md.Link __version__ f"https://github.com/pokurt/SCP-5170/commit/{__longVersion__}"))
                )))
        (await (message.reply
            text
            :reply_markup
                (bot.types.InlineKeyboardMarkup
                    [[(bot.types.InlineKeyboardButton :text "help" :callback_data "help_back")]])
            :disable_web_page_preview True))
        )
    )