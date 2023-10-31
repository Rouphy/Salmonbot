# Ctrl+Shift+F10以运行
# Ctrl+/以多行注释
# Ctrl+Alt+L以美化代码
# Help下拉菜单以重置licence
# 现在，开始你的表演吧！
import json
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, Event, Bot, MessageSegment
from nonebot.params import CommandArg
from pathlib import Path

help = on_command('help')


@help.handle()
async def _(args: Message = CommandArg()):
    arg = args.extract_plain_text()

    flag = False
    with open("./src/pics/plugins.json", 'r', encoding='utf-8') as fp:
        plugin_list = json.load(fp)
        fp.close()

    for i in plugin_list:
        if arg == i['plugin']:  # 判断help后面的选项是否存在于json表，否则返回默认帮助表
            flag = True
    if flag:
        await help.finish(MessageSegment.image(file=Path(f"./src/pics/{arg}.png")))
    else:
        await help.finish(MessageSegment.image(file=Path("./src/pics/help.png")))
