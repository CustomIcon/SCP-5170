# SCP-5170
### Pattern Screamer

## Project Structure
```
╭─ scp
├──── core / clients - filters - functions
├─────── # core files
├──── database
├─────── # a cache memory database
├──── plugins / bot - private - user
├─────── # the plugins directory
├──── utils
╰─────── # few helper scripts laying around for plugins
```

### Requirements
 - a brain
 - python>=3.8

### Setup
 - clone this repository with `git clone` with `--recrusive` flag and change directory to the root of the project
 - create a `venv` with `python -m venv venv` and activate the `venv`
 - install all modules in requirements with `python -m pip install -r requirements.txt` and `python -m pip install -r session/requirements.txt`
 - move config sample from `config.ini.sample` to `config.ini` and fill in the configs
 - create session for user and bot
   - user: `python -m session -s scp-user`
   - bot : `python -m session -s scp-bot -t {bot_token}`
 - all done. run the userbot with `python -m scp`

### Creating own modules
as you know SCP-5170 is using pyrogram and a custom client,
therefore a plugin can be very simple to make and import into `scp/plugins/private` directory:
```
scp.bot - bot client
scp.user - user client
scp.user.filters - pyrogram filters (for user client)
scp.bot.filters - pyrogram filters (for bot client)
scp.user.sudo - a filter with sudoers added
scp.bot.sudo - a different filter without pyrogram's filters.me for the bot client
scp.user.command - command filter for user
scp.bot.command - command filter for bot
```

 - an Example plugin the echo to a command with `(*prefix)hello`:
```
from scp import user

@user.on_message(
    user.sudo
    & user.command('hello')
    & user.filters.text
)
async def _(_, message: types.Message):
    await message.reply('hello')
```

### FAQ
- why given that name?
  the name speaks to itself, `the Pattern Screamer`

- sar please heroku...?
  first of all stop using heroku. use localhost, no need to pay. and you have the full control of it

- why does it look like kantek?
  i always loved it, therefore i did add KanteX to globally use in this userbot

### Special thancc
 - [Dan](https://github.com/delivrance) - pyrogram
 - [Fluffy Shark](https://github.com/ColinShark) - QR Code session generator Script
 - [Kneesocks](https://github.com/the-blank-x) - 13 year old with multiple police records (also eval module is originally by him)
 - [Davide Goggles](https://github.com/DavideGalilei) - spam check and automatic logging with extra pineapple toppings

and everyone who built awesome modules that are being used by this project
