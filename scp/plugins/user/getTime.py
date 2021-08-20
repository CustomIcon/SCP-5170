#XWSLLPX5RMIZ
from scp import user
from typing import List
import datetime


__PLUGIN__ = 'time'
__DOC__ = str(user.md.KanTeXDocument(
    user.md.Section('TimeDB scrapper',
        user.md.SubSection('time',
            user.md.Code('(*prefix)time {country_or_countryCode}')))))


@user.on_message(user.sudo & user.command('time'))
async def _(_, message: user.types.Message):
    if len(message.command) == 1:
        return None
    else:
        result = await genTime(
            message.command[1].lower(),
            ["zoneName", "countryName"]
        )
    if not result:
        return await message.reply(
            user.md.KanTeXDocument(
                user.md.Section('Error',
                user.md.Italic('location not found'))
            ), quote=True)
    await message.reply(result, quote=True, disable_web_page_preview=True)


async def genTime(
    to_find: str,
    findtype: List[str]
) -> str:
    data = await user.getRequest(
        "https://api.timezonedb.com/v2.1/list-time-zone?key=XWSLLPX5RMIZ&format=json&fields=countryCode,countryName,zoneName,gmtOffset,timestamp,dst",
    )

    for zone in data["zones"]:
        for eachtype in findtype:
            if to_find in zone[eachtype].lower():
                date_fmt = r"%d-%m-%Y"
                time_fmt = r"%H:%M:%S"
                day_fmt = r"%A"
                gmt_offset = zone["gmtOffset"]
                timestamp = datetime.datetime.now(
                    datetime.timezone.utc,
                ) + datetime.timedelta(seconds=gmt_offset)
                return user.md.KanTeXDocument(
                    user.md.Section('TimeDB Scrapper',
                        user.md.SubSection(zone["countryName"],
                            user.md.KeyValueItem(
                                user.md.Bold('zone_name'),
                                user.md.Code(zone["zoneName"])
                            ),
                            user.md.KeyValueItem(
                                user.md.Bold('ISO_code'),
                                user.md.Code(zone["countryCode"])
                            ),
                            user.md.KeyValueItem(
                                user.md.Bold('daylight_saving'),
                                user.md.Code('true' if zone["dst"] == 1 else 'false')
                            ),
                            user.md.KeyValueItem(
                                user.md.Bold('current_day'),
                                user.md.Code(timestamp.strftime(day_fmt))
                            ),
                            user.md.KeyValueItem(
                                user.md.Bold('current_time'),
                                user.md.Code(timestamp.strftime(time_fmt))
                                ),
                            user.md.KeyValueItem(
                                user.md.Bold('current_date'),
                                user.md.Code(timestamp.strftime(date_fmt))
                            ),
                            user.md.KeyValueItem(
                                user.md.Bold('time_zones'),
                                user.md.Link('here', 'https://en.wikipedia.org/wiki/List_of_tz_database_time_zones')
                            ),
                        ))
                )