from PIL import Image, ImageDraw, ImageFont
import random
import string
from io import BytesIO


def generate_captcha():
    """生成验证码图片 + 文本"""
    # 生成随机 4 位字符
    chars = random.choices(string.ascii_uppercase + string.digits, k=4)
    text = ''.join(chars)

    # 创建画布
    width, height = 120, 40
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()

    draw.text((10, 5), text, fill=(0, 0, 0), font=font)

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()

    return text, img_bytes
