def name_check(username: str = None):
    if username:
        return '@'+username
    return None


def bool_check(var: bool):
    if var:
        return "✅"
    else:
        return "❌"


def permissionParser(perms):
    text = ''
    text += 'Message: ' + bool_check(perms.can_send_messages) + '\n'
    text += 'Media: ' + bool_check(perms.can_send_media_messages) + '\n'
    text += 'Sticker: ' + bool_check(perms.can_send_stickers) + '\n'
    text += 'GIF: ' + bool_check(perms.can_send_animations) + '\n'
    text += 'Game: ' + bool_check(perms.can_send_games) + '\n'
    text += 'Inline: ' + bool_check(perms.can_use_inline_bots) + '\n'
    text += 'Web: ' + bool_check(perms.can_add_web_page_previews) + '\n'
    text += 'Poll: ' + bool_check(perms.can_send_polls) + '\n'
    text += 'Info: ' + bool_check(perms.can_change_info) + '\n'
    text += 'invite: ' + bool_check(perms.can_invite_users) + '\n'
    text += 'Pin: ' + bool_check(perms.can_pin_messages) + '\n'
    return text