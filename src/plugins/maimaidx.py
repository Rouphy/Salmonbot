import json
import os

from nonebot import on_command, on_regex
from nonebot.params import CommandArg, EventMessage
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from src.libraries.tool import hash
from src.libraries.maimaidx_music import *
from src.libraries.image import *
from src.libraries.maimai_best_40 import generate
from src.libraries.maimai_best_50 import generate50
import re


def song_txt(music: Music):
    return Message([
        MessageSegment("text", {
            "text": f"{music.id}. {music.title}\n"
        }),
        MessageSegment("image", {
            "file": f"https://www.diving-fish.com/covers/{get_cover_len5_id(music.id)}.png"
        }),
        MessageSegment("text", {
            "text": f"\n{'/'.join(music.level)}"
        })
    ])


def inner_level_q(ds1, ds2=None):
    result_set = []
    diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'ReM']
    if ds2 is not None:
        music_data = total_list.filter(ds=(ds1, ds2))
    else:
        music_data = total_list.filter(ds=ds1)
    for music in sorted(music_data, key=lambda i: int(i['id'])):
        for i in music.diff:
            result_set.append((music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
    return result_set


inner_level = on_command('inner_level ', aliases={'定数查歌 '})


@inner_level.handle()
async def _(event: Event, message: Message = CommandArg()):
    argv = str(message).strip().split(" ")
    if len(argv) > 2 or len(argv) == 0:
        await inner_level.finish("命令格式为\n定数查歌 <定数>\n定数查歌 <定数下限> <定数上限>")
        return
    if len(argv) == 1:
        result_set = inner_level_q(float(argv[0]))
    else:
        result_set = inner_level_q(float(argv[0]), float(argv[1]))
    if len(result_set) > 50:
        await inner_level.finish(f"结果过多（{len(result_set)} 条），请缩小搜索范围。")
        return
    s = ""
    for elem in result_set:
        s += f"{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})\n"
    await inner_level.finish(s.strip())


spec_rand = on_regex(r"^随个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?")


@spec_rand.handle()
async def _(event: Event, message: Message = EventMessage()):
    level_labels = ['绿', '黄', '红', '紫', '白']
    regex = "随个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, str(message).lower())
    try:
        if res.groups()[0] == "dx":
            tp = ["DX"]
        elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
            tp = ["SD"]
        else:
            tp = ["SD", "DX"]
        level = res.groups()[2]
        if res.groups()[1] == "":
            music_data = total_list.filter(level=level, type=tp)
        else:
            music_data = total_list.filter(level=level, diff=['绿黄红紫白'.index(res.groups()[1])], type=tp)
        if len(music_data) == 0:
            rand_result = "没有这样的乐曲哦。"
        else:
            rand_result = song_txt(music_data.random())
        await spec_rand.send(rand_result)
    except Exception as e:
        print(e)
        await spec_rand.finish("随机命令错误，请检查语法")


mr = on_regex(r".*maimai.*什么")


@mr.handle()
async def _():
    await mr.finish(song_txt(total_list.random()))


search_music = on_regex(r"^查歌.+")


@search_music.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = "查歌(.+)"
    name = re.match(regex, str(message)).groups()[0].strip()
    if name == "":
        return
    res = total_list.filter(title_search=name)
    if len(res) == 0:
        await search_music.send("没有找到这样的乐曲。")
    elif len(res) < 50:
        search_result = ""
        for music in sorted(res, key=lambda i: int(i['id'])):
            search_result += f"{music['id']}. {music['title']}\n"
        await search_music.finish(Message([
            MessageSegment("text", {
                "text": search_result.strip()
            })]))
    else:
        await search_music.send(f"结果过多（{len(res)} 条），请缩小查询范围。")


query_chart = on_regex(r"^([绿黄红紫白]?)id([0-9]+)")


@query_chart.handle()
async def _(event: Event, message: Message = EventMessage()):
    regex = "([绿黄红紫白]?)id([0-9]+)"
    groups = re.match(regex, str(message)).groups()
    level_labels = ['绿', '黄', '红', '紫', '白']
    if groups[0] != "":
        try:
            level_index = level_labels.index(groups[0])
            level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re: MASTER']
            name = groups[1]
            music = total_list.by_id(name)
            chart = music['charts'][level_index]
            ds = music['ds'][level_index]
            level = music['level'][level_index]
            file = f"https://www.diving-fish.com/covers/{get_cover_len5_id(music['id'])}.png"
            if len(chart['notes']) == 4:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
BREAK: {chart['notes'][3]}
谱师: {chart['charter']}'''
            else:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
TOUCH: {chart['notes'][3]}
BREAK: {chart['notes'][4]}
谱师: {chart['charter']}'''
            await query_chart.send(Message([
                MessageSegment("text", {
                    "text": f"{music['id']}. {music['title']}\n"
                }),
                MessageSegment("image", {
                    "file": f"{file}"
                }),
                MessageSegment("text", {
                    "text": msg
                })
            ]))
        except Exception:
            await query_chart.send("未找到该谱面")
    else:
        name = groups[1]
        music = total_list.by_id(name)
        try:
            file = f"https://www.diving-fish.com/covers/{get_cover_len5_id(music['id'])}.png"
            await query_chart.send(Message([
                MessageSegment("text", {
                    "text": f"{music['id']}. {music['title']}\n"
                }),
                MessageSegment("image", {
                    "file": f"{file}"
                }),
                MessageSegment("text", {
                    "text": f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}"
                })
            ]))
        except Exception:
            await query_chart.send("未找到该乐曲")


wm_list = ['拼机', '推分', '越级', '下埋', '夜勤', '练底力', '练手法', '打旧框', '干饭', '抓绝赞', '收歌']

jrwm = on_command('今日舞萌', aliases={'今日mai'})


@jrwm.handle()
async def _(event: Event, message: Message = CommandArg()):
    qq = int(event.get_user_id())
    h = hash(qq)
    rp = h % 100
    wm_value = []
    for i in range(11):
        wm_value.append(h & 3)
        h >>= 2
    s = f"今日人品值：{rp}\n"
    for i in range(11):
        if wm_value[i] == 3:
            s += f'宜 {wm_list[i]}\n'
        elif wm_value[i] == 0:
            s += f'忌 {wm_list[i]}\n'
    s += "三文鱼翻了个身并拿出了\n今日推荐歌曲："
    music = total_list[h % len(total_list)]
    await jrwm.finish(Message([MessageSegment("text", {"text": s})] + song_txt(music)))


query_score = on_command('分数线')


@query_score.handle()
async def _(event: Event, message: Message = CommandArg()):
    r = "([绿黄红紫白])(id)?([0-9]+)"
    argv = str(message).strip().split(" ")
    if len(argv) == 1 and argv[0] == '帮助':
        s = '''此功能为查找某首歌分数线设计。
命令格式：分数线 <难度+歌曲id> <分数线>
例如：分数线 紫799 100
命令将返回分数线允许的 TAP GREAT 容错以及 BREAK 50落等价的 TAP GREAT 数。
以下为 TAP GREAT 的对应表：
GREAT/GOOD/MISS
TAP\t1/2.5/5
HOLD\t2/5/10
SLIDE\t3/7.5/15
TOUCH\t1/2.5/5
BREAK\t5/12.5/25(外加200落)'''
        await query_score.send(Message([
            MessageSegment("image", {
                "file": f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"
            })
        ]))
    elif len(argv) == 2:
        try:
            grp = re.match(r, argv[0]).groups()
            level_labels = ['绿', '黄', '红', '紫', '白']
            level_labels2 = ['Basic', 'Advanced', 'Expert', 'Master', 'Re:MASTER']
            level_index = level_labels.index(grp[0])
            chart_id = grp[2]
            line = float(argv[1])
            music = total_list.by_id(chart_id)
            chart: Dict[Any] = music['charts'][level_index]
            tap = int(chart['notes'][0])
            slide = int(chart['notes'][2])
            hold = int(chart['notes'][1])
            touch = int(chart['notes'][3]) if len(chart['notes']) == 5 else 0
            brk = int(chart['notes'][-1])
            total_score = 500 * tap + slide * 1500 + hold * 1000 + touch * 500 + brk * 2500
            break_bonus = 0.01 / brk
            break_50_reduce = total_score * break_bonus / 4
            reduce = 101 - line
            if reduce <= 0 or reduce >= 101:
                raise ValueError
            await query_chart.send(f'''{music['title']} {level_labels2[level_index]}
分数线 {line}% 允许的最多 TAP GREAT 数量为 {(total_score * reduce / 10000):.2f}(每个-{10000 / total_score:.4f}%),
BREAK 50落(一共{brk}个)等价于 {(break_50_reduce / 100):.3f} 个 TAP GREAT(-{break_50_reduce / total_score * 100:.4f}%)''')
        except Exception:
            await query_chart.send("格式错误，输入“分数线 帮助”以查看帮助信息")


best_40_pic = on_command('b40')


@best_40_pic.handle()
async def _(event: Event, message: Message = CommandArg()):
    username = str(message).strip()
    if username == "":
        payload = {'qq': str(event.get_user_id())}
    else:
        payload = {'username': username}
    img, success = await generate(payload)
    if success == 400:
        await best_40_pic.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。查分器网址：https://www.diving-fish.com/maimaidx/prober/")
    elif success == 403:
        await best_40_pic.send("该用户禁止了其他人获取数据。")
    else:
        await best_40_pic.send(Message([
            MessageSegment("image", {
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            })
        ]))


best_50_pic = on_command('b50', aliases={'逼五菱','比五菱','逼武林','逼舞林'})


@best_50_pic.handle()
async def _(event: Event, message: Message = CommandArg()):
    username = str(message).strip()
    if username == "":
        payload = {'qq': str(event.get_user_id()), 'b50': True}
    else:
        payload = {'username': username, 'b50': True}
    img, success = await generate50(payload)
    if success == 400:
        await best_50_pic.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。查分器网址：https://www.diving-fish.com/maimaidx/prober/")
    elif success == 403:
        await best_50_pic.send("该用户禁止了其他人获取数据。")
    else:
        await best_50_pic.send(Message([
            MessageSegment("image", {
                "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            })
        ]))


get_avg = on_regex('^平均值([绿黄红紫白]?)id([0-9]+)')


@get_avg.handle()
async def _(message: Message = EventMessage()):
    regex = '平均值([绿黄红紫白]?)id([0-9]+)'
    groups = re.match(regex, str(message)).groups()
    music_info = total_list.by_id(groups[1])
    music_avg = requests.get("https://www.diving-fish.com/api/maimaidxprober/chart_stats").json()
    level_label = ['绿', '黄', '红', '紫', '白']
    msg = '出错了，检查一下你的指令吧'
    try:
        if groups[0] != '':
            level_index = level_label.index(groups[0])
            music = music_avg[str(groups[1])][level_index]
            msg = f'''{music_info['title']}({groups[0]})一共被游玩了{music['count']}次
平均达成率为{round(music['avg'], 4)}%
一共被鸟加了{music['sssp_count']}次'''
            await get_avg.send(msg)
        else:
            music = music_avg[str(groups[1])]
            msg = f'{music_info["id"]}.{music_info["title"]}\n'
            for i in range(0, len(music)):
                if len(music[i]) != 0:
                    msg += f"{level_label[i]}:平均达成率:{round(music[i]['avg'], 4)}%,鸟加次数:{music[i]['sssp_count']}\n"
            await get_avg.send(msg.strip())
    except Exception as e:
        print(e)
        await get_avg.finish(msg.strip())


add_oname = on_regex(r'添加别名 [0-9]+ .+')


@add_oname.handle()
async def _(message: Message = EventMessage()):
    info = re.match("添加别名 ([0-9]+) (.+)", str(message)).groups()
    alias = info[1]  # 用户提交的别名
    id = info[0]  # 用户提交的别名id
    with open("./src/musicAliases.json", 'r', encoding='utf-8') as fp:
        music_list = json.load(fp)  # 读入json表传给music_list
        fp.close()
    flag = False
    for music in music_list:  # 遍历json表

        # if alias in music['alias']:
        #     await add_oname.finish("别名存在")
        # if str(music['id']) == id:  # 查对应id
        #     flag = True
        #     music['alias'].append(alias)  # 添加别名

        for i in music['alias']:
            if str(music['id']) == id:
                if alias in music['alias']:
                    await add_oname.finish("别名存在")
                else:
                    flag = True
                    music['alias'].append(alias)
                    break

    if flag:
        with open("./src/musicAliases.json", 'w', encoding='utf-8') as fp:
            fp.write(json.dumps(music_list, ensure_ascii=False))
            await add_oname.finish("添加成功")
    else:
        if total_list.by_id(id) is None:
            await add_oname.finish("id不存在")
        else:
            music_list.append(
                {
                    "id": int(id),
                    "title": total_list.by_id(id)['title'],
                    "alias": [alias]
                }
            )
            music_list.sort(key=lambda a: a['id'])
            with open("./src/musicAliases.json", 'w', encoding='utf-8') as fp:
                fp.write(json.dumps(music_list, ensure_ascii=False, indent=4))
                await add_oname.finish("添加成功")


find_name = on_regex(".+是什么歌")


@find_name.handle()
async def _(message: Message = EventMessage()):
    info = re.match("(.+)是什么歌", str(message)).groups()
    title = info[0]
    with open("./src/musicAliases.json", 'r', encoding='utf-8') as fp:
        music_list = json.load(fp)
        fp.close()

    flag = 0
    result = []
    resultStr = ""
    for music in music_list:

        # if title in music['alias']:
        #     music = total_list.by_id(str(music['id']))
        #     file = f"https://www.diving-fish.com/covers/{get_cover_len5_id(music['id'])}.png"
        #     await find_name.finish(Message([
        #         MessageSegment("text", {
        #             "text": f"{music['id']}. {music['title']}\n"
        #         }),
        #         MessageSegment("image", {
        #             "file": f"{file}"
        #         }),
        #         MessageSegment("text", {
        #             "text": f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}"
        #         })
        #     ]))

        for alias in music['alias']:
            if title == alias:
                flag += 1
                result.append(music['id'])
    if flag == 0:
        await find_name.finish("未找到该乐曲")
    elif flag == 1:
        music = total_list.by_id(str(result[0]))  # music type: dictionary
        file = f"https://www.diving-fish.com/covers/{get_cover_len5_id(music['id'])}.png"
        await find_name.finish(Message([
            MessageSegment("text", {
                "text": f"{music['id']}. {music['title']}\n"
            }),
            MessageSegment("image", {
                "file": f"{file}"
            }),
            MessageSegment("text", {
                "text": f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}"
            })
        ]))
    elif flag > 1:
        for i in result:
            music = total_list.by_id(str(i))
            resultStr += "%d.%s\n" % (i, music['title'])
        await find_name.finish(Message([
            MessageSegment("text", {
                "text": f"{title}包含多个结果：\n{resultStr}"
            })
        ]))


del_oname = on_regex(r"删除别名 .+")


@del_oname.handle()
async def _(message: Message = EventMessage()):
    info = re.match("删除别名 ([0-9]+) (.+)", str(message)).groups()
    title = info[1]
    id = info[0]
    with open("./src/musicAliases.json", 'r', encoding='utf-8') as fp:
        music_list = json.load(fp)
        fp.close()


    flag = False
    for music in music_list:
        # if title in music['alias']:
        #     music['alias'].remove(title)
        #     with open("./src/musicAliases.json", 'w', encoding='utf-8') as fp:
        #         fp.write(json.dumps(music_list, ensure_ascii=False, indent=4))
        #         fp.close()
        #     await del_oname.finish("删除成功")

        for i in music['alias']:
            if id == str(music['id']):
                if title in music['alias']:
                    music['alias'].remove(title)
                    flag = True
                    break
                else:
                    await del_oname.finish("未找到别名")
    if flag:
        with open("./src/musicAliases.json", 'w', encoding='utf-8') as fp:
            fp.write(json.dumps(music_list, ensure_ascii=False, indent=4))
            fp.close()
        await del_oname.finish("删除成功")
    else:
        await del_oname.finish("id不存在")


find_alias = on_regex(".+有什么别名")


@find_alias.handle()
async def _(message: Message = EventMessage()):
    info = re.match("(.+)有什么别名", str(message)).groups()
    id = info[0]
    flag = False
    resultStr = ""
    with open("./src/musicAliases.json", 'r', encoding='utf-8') as fp:
        music_list = json.load(fp)  # 读入json表传给music_list
        fp.close()
    for music in music_list:
        if id == str(music['id']):
            flag = True
            for alias in music['alias']:
                resultStr += "\n%s" % alias

    if flag:
        await find_alias.finish(Message([
            MessageSegment("text", {
                "text": f"id{id}有以下别名：{resultStr}"
            })
        ]))
    else:
        await find_alias.finish("id不存在")


suggest = on_command('鸟加推荐')


# 根据rating推荐可鸟加歌曲(每日更新)
@suggest.handle()
async def _(event: Event, message: Message = CommandArg()):
    diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'ReM']
    payload = {'qq': str(event.get_user_id()), 'b50': True}
    rating, rating_sd, rating_dx = await getRating(payload)
    if (rating == None):
        if rating_sd == 400:
            await best_40_pic.send("你疑似没有绑定查分器")
    avg_sd, avg_dx = rating_sd // 35, rating_dx // 15
    ds_sd, ds_dx = round(avg_sd / 22.4, 1), round(avg_dx / 22.4, 1)
    musics = total_list
    # 推荐定数浮动范围
    result_sd, result_dx = musics.filter(ds=(ds_sd - 0.1, ds_sd + 0.2), type='SD'), musics.filter(
        ds=(ds_dx - 0.1, ds_dx + 0.3), type='DX')
    random.seed(datetime.now().strftime("%Y%m%d"))
    # 标准乐谱 和 DX乐谱 歌曲推荐数量
    sd_sample, dx_sample = random.sample(result_sd, 3), random.sample(result_dx, 3)
    sd_result, dx_result = [], []
    for music in sorted(sd_sample, key=lambda i: int(i['id'])):
        for i in music.diff:
            sd_result.append((music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
    for music in sorted(dx_sample, key=lambda i: int(i['id'])):
        for i in music.diff:
            dx_result.append((music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
    s1 = "sd:\n"
    for elem in sd_result:
        s1 += f"{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})\n"
    s2 = "dx:\n"
    for elem in dx_result:
        s2 += f"{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})\n"
    await suggest.finish(("今日鸟加推荐:\n" + s1 + s2).rstrip())


guess = on_command("猜歌")


@guess.handle()
async def _(matcher: Matcher):
    music_list = total_list
    music = music_list.random()
    id = music['id']
    # 读取封面图片
    image = Image.open("./src/static/mai/cover/" + str(id).rjust(5, "0") + ".png")
    # 随机裁切
    height, width = image.size
    # 这里写死了是裁切1/5，也就是截取封面的1/25，可以调整改变难度
    h, w = height // 4, width // 4
    h_s, w_s = random.randint(0, height - h), random.randint(0, width - w)
    image_crop = image.crop((w_s, h_s, w_s + w, h_s + h))
    matcher.set_arg('music', music)
    # 回答正确返回
    matcher.set_arg('right', Message([
        MessageSegment("text", {
            "text": "恭喜猜对了，答案是\n"
        }),
        MessageSegment("text", {
            "text": f"{music.id}. {music.title}\n"
        }),
        MessageSegment("image", {
            "file": f"https://www.diving-fish.com/covers/{get_cover_len5_id(music.id)}.png"
        }),
    ]))
    # 结束返回
    matcher.set_arg('over', Message([
        MessageSegment("text", {
            "text": "逊欸，是这首歌\n"
        }),
        MessageSegment("text", {
            "text": f"{music.id}. {music.title}\n"
        }),
        MessageSegment("image", {
            "file": f"https://www.diving-fish.com/covers/{get_cover_len5_id(music.id)}.png"
        }),
    ]))
    await guess.send(Message([
        MessageSegment("text", {
            "text": "输入歌曲id(dx与sd区分，两个都试一下),歌名或者别名"
        }),
        MessageSegment("image", {
            "file": f"base64://{str(image_to_base64(image_crop), encoding='utf-8')}"
        })
    ]))
    print(music)  # 狗修金专用外挂


@guess.got("res")
async def _(matcher: Matcher, res=ArgPlainText()):
    flag = False
    music = matcher.get_arg("music")
    song = None
    with open("./src/musicAliases.json", 'r', encoding='utf-8') as alias:
        for s in json.load(alias):
            if music.id == str(s["id"]):
                song = s
                break
    if song is not None and res in song["alias"]:
        flag = True
    # 成功条件，可以更换条件比如别名xx
    if res == music.id or res == music.title or flag:
        await guess.finish(matcher.get_arg("right"))
    elif res == "/结束":
        await guess.finish(matcher.get_arg("over"))
    else:
        await guess.reject(random.sample(["猜错了,要不再想想？", "杂鱼~♡，杂鱼~♡，猜错歌的杂鱼~♡", "错了，速速艾草"], 1)[0])