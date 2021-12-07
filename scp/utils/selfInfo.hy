(import scp)

(setv info {})

(defn/a updateInfo []
    (setv u (await (scp.user.get_me)))
    (setv b (await (scp.bot.get_me)))
    (assoc info "_user_id" u.id
        "_user_username" u.username
        "_bot_id" b.id
        "_bot_username" b.username))
