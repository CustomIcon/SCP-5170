from scp import user
from scp.utils.cache import Messages
from typing import List
from scp.utils.parser import getAttr
from scp.utils.MessageTypes import getType, Types


@user.on_message(~user.filters.me)
async def _(_, message: user.types.Message):
    Messages.append(message)


SendType = {
    'Text': user.send_message,
    'Sticker': user.send_sticker,
    "Document": user.send_document,
    'Photo': user.send_photo,
    'Audio': user.send_audio,
    'Voice': user.send_voice,
    'Video': user.send_video
}


@user.on_deleted_messages(~user.filters.private & ~user.filters.me)
async def _(client: user, messages: List):
    for mDel in messages:
        for message in Messages:
            if (
                mDel.chat.id == message.chat.id
                and mDel.message_id == message.message_id
            ):
                dataType, content, caption= getType(message)
                text = user.md.KanTeXDocument(
                            user.md.Section(
                                '#DeletedMessage',
                                user.md.SubSection(
                                    message.chat.title,
                                    user.md.KeyValueItem(
                                        user.md.Bold('chat_id'),
                                        user.md.Code(
                                            message.chat.id,
                                        ),
                                    ),
                                    user.md.KeyValueItem(
                                        user.md.Bold(
                                            'user_id',
                                        ),
                                        user.md.Code(
                                            getAttr(
                                                message,
                                                ['from_user', 'sender_chat']).id
                                            ),
                                    ),
                                    user.md.KeyValueItem(
                                        user.md.Bold('message_id'),
                                        user.md.Code(
                                            message.message_id,
                                        ),
                                    ),
                                    user.md.KeyValueItem(
                                        user.md.Bold('content'),
                                        user.md.Code(
                                            f'\n{content}',
                                        ),
                                    ),
                                    user.md.KeyValueItem(
                                        user.md.Bold('caption(media)'),
                                        user.md.Code(
                                            f'\n{caption}',
                                        ),
                                    ),
                                ),
                            ),
                        )
                if dataType == Types.TEXT:
                    await SendType['Text'](user.log_channel, text)
                elif dataType == Types.STICKER:
                    await SendType['Sticker'](user.log_channel, content)
                    await SendType['Text'](user.log_channel, text)
                elif dataType == Types.DOCUMENT:
                   await SendType['Document'](user.log_channel, content, caption=text)
                elif dataType == Types.PHOTO:
                    await SendType['Document'](user.log_channel, content, caption=text)
                elif dataType == Types.AUDIO:
                    await SendType['Audio'](user.log_channel, content, caption=text)
                elif dataType == Types.VOICE:
                    await SendType['Voice'](user.log_channel, content, caption=text)
                elif dataType == Types.VIDEO:
                    await SendType['Video'](user.log_channel, content, caption=text)