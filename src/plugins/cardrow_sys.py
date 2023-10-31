# Ctrl+Shift+F10以运行
# Ctrl+/以多行注释
# Ctrl+Alt+L以美化代码
# Help下拉菜单以重置licence
# 现在，开始你的表演吧！
import json

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot, MessageSegment
from nonebot.params import CommandArg
import time

addcard = on_command("hop卡数", aliases={"hop"})


@addcard.handle()
async def jk(event: MessageEvent, args: Message = CommandArg()):
    with open("./src/log.json", 'r', encoding='utf-8') as fp:
        log = json.load(fp)
        fp.close()
    t = time.strftime("%H:%M:%S", time.localtime())
    sender = event.sender.card or event.sender.nickname
    if log:
        latest = log[-1]
        if args == "++" or args == "+1":
            latest = latest['count'] + 1
            log.append({
                "name": sender,
                "time": t,
                "count": latest
            })
            with open("./src/log.json", 'w', encoding='utf-8') as fp:
                fp.write(json.dumps(log, ensure_ascii=False, indent=4))
            await addcard.finish(Message([
                MessageSegment("text", {
                    "text": f"添加成功！当前机厅卡数：{latest}"
                })
            ]))
    elif args == "++" or args == "+1":
        log.append({
            "name": sender,
            "time": t,
            "count": 1
        })
        latest = 1
        with open("./src/log.json", 'w', encoding='utf-8') as fp:
            fp.write(json.dumps(log, ensure_ascii=False, indent=4))
        await addcard.finish(Message([
            MessageSegment("text", {
                "text": f"添加成功！当前机厅卡数：1"
            })
        ]))


cardcount = on_command("几卡", aliases={"j"})


@cardcount.handle()
async def j():
    pass
