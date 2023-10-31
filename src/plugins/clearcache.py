# Ctrl+Shift+F10以运行
# Ctrl+/以多行注释
# Ctrl+Alt+L以美化代码
# Help下拉菜单以重置licence
# 现在，开始你的表演吧！

from os import remove, listdir
from re import search
from nonebot import on_command
from nonebot.permission import SUPERUSER

clear_cache = on_command('clearcache', permission=SUPERUSER)


@clear_cache.handle()
async def _():
    ls = listdir("./cqhttp/data/cache")  # 返回缓存目录文件列表
    flag = False
    for i in ls:
        file = search(r"^[a-f0-9]+(\.cache)$", i)
        if file:
            remove(f"./cqhttp/data/cache/{i}")
            flag = True

    if flag:
        await clear_cache.finish("缓存清除成功")
    else:
        await clear_cache.finish("当前无缓存")
