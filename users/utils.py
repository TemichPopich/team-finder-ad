import hashlib
import io

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

# Avatar color constants (RGB tuples)
AVATAR_COLOR_ROYAL_BLUE = (65, 105, 225)
AVATAR_COLOR_FOREST_GREEN = (34, 139, 34)
AVATAR_COLOR_CRIMSON = (220, 20, 60)
AVATAR_COLOR_DARK_ORANGE = (255, 140, 0)
AVATAR_COLOR_DARK_ORCHID = (148, 0, 211)
AVATAR_COLOR_DARK_CYAN = (0, 139, 139)
AVATAR_COLOR_DARK_ORCHID_PINK = (218, 112, 214)
AVATAR_COLOR_STEEL_BLUE = (70, 130, 180)
AVATAR_COLOR_LIME_GREEN = (50, 205, 50)
AVATAR_COLOR_TOMATO = (255, 99, 71)

AVATAR_COLORS = [
    AVATAR_COLOR_ROYAL_BLUE,
    AVATAR_COLOR_FOREST_GREEN,
    AVATAR_COLOR_CRIMSON,
    AVATAR_COLOR_DARK_ORANGE,
    AVATAR_COLOR_DARK_ORCHID,
    AVATAR_COLOR_DARK_CYAN,
    AVATAR_COLOR_DARK_ORCHID_PINK,
    AVATAR_COLOR_STEEL_BLUE,
    AVATAR_COLOR_LIME_GREEN,
    AVATAR_COLOR_TOMATO,
]

AVATAR_SIZE = 200
AVATAR_TEXT_COLOR = (255, 255, 255)
AVATAR_FORMAT = 'PNG'


def generate_avatar(user):
    """Generate avatar with first letter of name on colored background."""
    size = (AVATAR_SIZE, AVATAR_SIZE)
    background_color = _get_random_color(user.email)

    img = Image.new('RGB', size, color=background_color)
    draw = ImageDraw.Draw(img)

    initial = user.name[0].upper() if user.name else '?'

    font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), initial, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), initial, fill=AVATAR_TEXT_COLOR, font=font)

    buffer = io.BytesIO()
    img.save(buffer, format=AVATAR_FORMAT)
    buffer.seek(0)

    filename = f"avatar_{hashlib.md5(user.email.encode()).hexdigest()}.png"
    user.avatar.save(filename, ContentFile(buffer.read()), save=False)


def _get_random_color(email):
    """Get a random pleasant background color based on email hash."""
    hash_val = int(hashlib.md5(email.encode()).hexdigest(), 16)
    return AVATAR_COLORS[hash_val % len(AVATAR_COLORS)]
