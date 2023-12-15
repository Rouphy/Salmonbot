import base64
from io import BytesIO

from PIL import Image
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.plugin.on import on_keyword

daisuke = on_keyword({"daisuke", "快关浴霸"})


@daisuke.handle()
async def _():
    img = Image.open('src/pics/daisuke.png')
    await daisuke.finish(MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))


def image_to_base64(img, format='PNG'):
    output_buffer = BytesIO()
    img.save(output_buffer, format)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str
