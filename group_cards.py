import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import card_manager


TEXT_COLOR = (255, 255, 255)


CARD_WIDTH = 500 // 2
CARD_HEIGHT = int(CARD_WIDTH / 0.79945)
GAP = 50 // 2
FONT_SIZE = 50 // 2
LIST_GAP = 10 // 2

CARD_IMAGES_DIRECTORY = "cards"
ASSET_DIRECTORY = "assets"

# if relative doesn't work use absolute
FONT_PATH = "lemon_milk/LEMONMILK-Medium.otf"

font = ImageFont.truetype(
    FONT_PATH,
    FONT_SIZE
)

_, top_font_offset = font.getmetrics()


HEHET_ID = -1
BUD_ID = -2

# small images, for text
HEHET_IMAGE = Image.open(
    os.path.join(ASSET_DIRECTORY, "hehet.png")
).resize(
    (FONT_SIZE, FONT_SIZE)
).convert("RGBA")

BUD_IMAGE = Image.open(
    os.path.join(ASSET_DIRECTORY, "bud.png")
).resize(
    (FONT_SIZE, FONT_SIZE)
).convert("RGBA")

# big images, for display
BIG_HEHET_IMAGE = Image.open(
    os.path.join(ASSET_DIRECTORY, "hehet.png")
).resize(
    (CARD_WIDTH, CARD_WIDTH)
).convert("RGBA")


# big images, for display
BIG_BUD_IMAGE = Image.open(
    os.path.join(ASSET_DIRECTORY, "bud.png")
).resize(
    (CARD_WIDTH, CARD_WIDTH)
).convert("RGBA")

def generate_image(
        displayed: list[str],
        output: str | os.PathLike | BytesIO,
        text: bool = False,
        list_items: bool = False
    ) -> BytesIO:

    width = min(len(displayed), 5)
    height = 1 + (len(displayed) - 1) // 5

    total_width = width * (GAP + CARD_WIDTH) + GAP
    total_height = height * (GAP + CARD_HEIGHT) + GAP

    if text:
        total_height += height * FONT_SIZE

    list_text_offset = 0
    if list_items:
        hehet = sum([i[1] for i in displayed if i[0] == HEHET_ID])
        buds = sum([i[1] for i in displayed if i[0] == BUD_ID])

        _displayed = []
        if hehet != 0:
            _displayed.append([HEHET_ID, f"{hehet:,}"])

        if buds != 0:
            _displayed.append([BUD_ID, f"{buds:,}"])

        cards = [i[1] for i in displayed if i[0] not in [HEHET_ID, BUD_ID]]
        cards_count = dict.fromkeys(
            cards,
            0
        )

        for card in cards:
            cards_count[card] += 1

        for card, count in cards_count.items():
            _displayed.append([1, f"x{count} {card.upper()}"])

        list_text_offset = len(_displayed) * FONT_SIZE + (len(_displayed) - 1) * LIST_GAP


        item_list = [[i, f"• {v}"] for i, v  in _displayed]

    total_height += list_text_offset


    img = Image.new(
    "RGBA",
        (
            total_width,
            total_height
        ),
        color = (0, 0, 0, 0)
    )

    draw = ImageDraw.ImageDraw(img)

    if list_items:
        y = 0
        for i, v in item_list:
            if i == HEHET_ID:
                text_width = int(font.getlength(v))
                img.paste(
                    HEHET_IMAGE,
                    (GAP + text_width, y + top_font_offset)
                )
            elif i == BUD_ID:
                text_width = int(font.getlength(v))
                img.paste(
                    BUD_IMAGE,
                    (GAP + text_width, y + top_font_offset)
                )

            draw.text(
                (GAP, y),
                text = v,
                fill = TEXT_COLOR,
                font = font
            )

            y += FONT_SIZE + LIST_GAP


    for i, info in enumerate(displayed):
        _id, displayed_text = info
        if isinstance(displayed_text, int):
            displayed_text = "{:,}".format(displayed_text)

        if _id == HEHET_ID:
            pasted_image = BIG_HEHET_IMAGE
        elif _id == BUD_ID:
            pasted_image = BIG_BUD_IMAGE
        else:
            pasted_image = Image.open(card_manager.get_card_image_from_id(displayed_text)).resize((CARD_WIDTH, CARD_HEIGHT))

        y, x = divmod(i, 5)
        # not centered
        _position = (
            GAP + x * (CARD_WIDTH + GAP),
            GAP + y * (CARD_HEIGHT + GAP + (FONT_SIZE * text)) + list_text_offset
        )

        # centered
        position = (
            _position[0] + CARD_WIDTH // 2 - pasted_image.width // 2,
            _position[1] + CARD_HEIGHT // 2 - pasted_image.height // 2,
        )


        img.paste(pasted_image, position)
        if text:
            text_width = font.getlength(displayed_text)
            text_position = (
                _position[0] + CARD_WIDTH // 2 - text_width // 2,
                _position[1] + CARD_HEIGHT
            )


            if _id in [BUD_ID, HEHET_ID]:
                displayed_text = f"x {displayed_text}"
            else:
                displayed_text = f"x1 {displayed_text}"

            draw.text(
                text_position,
                text = displayed_text,
                fill = TEXT_COLOR,
                font = font
            )

    img.save(output, "png")


if __name__ == "__main__":
    generate_image(
        [
            [HEHET_ID, 1200],
            [1, "ASHDKK"],
            [HEHET_ID, 10_000],
            [1, "DSTYJN"],
            [HEHET_ID, 9450],
            [1, "DSTYJN"],
        ],
        "rat.png",
        text = True,
        list_items = True)
