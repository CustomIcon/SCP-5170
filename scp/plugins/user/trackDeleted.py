from scp import user
from scp.utils.cache import Messages  # type: ignore
from typing import List
from scp.utils.parser import getAttr
from scp.utils.MessageTypes import getType, Types  # type: ignore
import asyncio


@user.on_message(
    ~user.filters.me
    & ~user.filters.service,
)
async def _(_, message: user.types.Message):
    Messages.append(message)


SendType = {
    'Text': user.send_message,
    'Sticker': user.send_sticker,
    'Document': user.send_document,
    'Photo': user.send_photo,
    'Audio': user.send_audio,
    'Voice': user.send_voice,
    'Video': user.send_video,
}


@user.on_deleted_messages(
    ~user.filters.private
    & ~user.filters.me
    & ~user.filters.service,
)
async def _(_, messages: List):
    for mDel in messages:
        for message in Messages:
            if (
                mDel.chat.id == message.chat.id
                and mDel.message_id == message.message_id
            ):
                dataType, content, caption = getType(message)
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
                                        ['from_user', 'sender_chat'],
                                    ).id,
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
                            ) if message.caption else None,
                        ),
                    ),
                )
                return await dataTypeCheck(
                    dataType,
                    content,
                    text,
                )


async def dataTypeCheck(
    dataType: int,
    content: str,
    text: user.md.KanTeXDocument,
):
    if dataType == Types.TEXT:
        return await SendType['Text'](
            user.log_channel,
            text,
        )
    elif dataType == Types.STICKER:
        await SendType['Sticker'](
            user.log_channel,
            content,
        )
        return await SendType['Text'](
            user.log_channel,
            text,
        )
    elif dataType == Types.DOCUMENT:
        return await SendType['Document'](
            user.log_channel,
            content,
            caption=text,
        )
    elif dataType == Types.PHOTO:
        return await SendType['Photo'](
            user.log_channel,
            content,
            caption=text,
        )
    elif dataType == Types.AUDIO:
        await SendType['Audio'](
            user.log_channel,
            content,
            caption=text,
        )
    elif dataType == Types.VOICE:
        return await SendType['Voice'](
            user.log_channel,
            content,
            caption=text,
        )
    elif dataType == Types.VIDEO:
        return await SendType['Video'](
            user.log_channel,
            content,
            caption=text,
        )


async def clearMessages(
    seconds=172800  # 2 days
):
    while not await asyncio.sleep(seconds):
        print(len(Messages))
        Messages.clear()


asyncio.create_task(clearMessages())
