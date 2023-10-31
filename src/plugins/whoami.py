# Ctrl+Shift+F10以运行
# Ctrl+/以多行注释
# Ctrl+Alt+L以美化代码
# Help下拉菜单以重置licence
# 现在，开始你的表演吧！

import random

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message

hello = on_command("三文鱼", aliases={"Salmon", "鱼仔", "鱼宝"})
ans = ["喵", "在呢~", "想我了吗？", "我不能吃"]


@hello.handle()
async def _():
    # await hello.finish(Message("在呢~"))

    i = random.randint(1, len(ans))
    await hello.finish(Message(ans[i - 1]))
