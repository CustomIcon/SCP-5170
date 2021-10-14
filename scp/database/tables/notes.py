from scp import user
import json
from .import checkTable


class Notes:
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ) -> None:
        self.key = key
        self.value = value

    async def load(
        self
    ):
        tableID = await checkTable('notes')
        msg = await user.get_messages(
            chat_id=user._config.getint(
                '.internal',
                'databasechannel',
            ),
            message_ids=tableID,
        )
        if msg:
            return json.loads(msg.text)
        return {}

    async def dump(self, data: dict):
        final = json.dumps(data)
        await user.edit_message_text(
            chat_id=user._config.getint('.internal', 'databasechannel'),
            message_id=user._config.getint('.internal', 'notes'),
            text=f'```{final}```',
            parse_mode='markdown',
        )
