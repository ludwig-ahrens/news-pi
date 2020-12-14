#!/bin/python3

from cairosvg import svg2png
from io import BytesIO
import json
import os
from PIL import Image, ImageDraw, ImageFont

from datum import Datum
import tagesschau as ts
from weather import OpenWeather

DIR = os.path.dirname(os.path.realpath(__file__))
PNG_DIR = os.path.join(DIR, "pngs")
CONFIG_FILE = os.path.join(DIR, "config.json")

IMAGE_SIZE = (448, 600)
WHITE = 0
RED = 1
BLACK = 2
PALETTE = [255, 255, 255, 200, 0, 0, 0, 0, 0]
MARGIN_X = 10
MARGIN_Y = 10
fonts = {}


class Drawer:
    def __init__(self):
        with open(CONFIG_FILE) as f:
            config = json.loads(f.read())
        self.open_weather = OpenWeather(config["open_weather"])
        self.tagesschau = ts.TagesschauService(3, 1, 1)
        self.datum = Datum(config["birthdays"], config["events"])

    def render(self):
        self.image = Image.new("P", IMAGE_SIZE, 0)
        self.image.putpalette(PALETTE)
        self.draw = ImageDraw.ImageDraw(self.image)

        _, y_date = self.date()
        y_weather = self.weather()
        y = max(y_date, y_weather) + MARGIN_Y
        y = self.birthday_wishes(y)
        self.news(y)

        return self.image

    def birthday_wishes(self, y):
        names = self.datum.birthdays()
        if len(names) == 0:
            return y
        wishes = self.datum.birthday_wishes(names)
        _, y_range = self.draw_texts(
            [wishes],
            [40],
            colors=[BLACK],
            y_range=(y + 10, IMAGE_SIZE[1] - MARGIN_Y),
            x_aligns=[1],
        )
        return y_range[1]

    def date(self):
        wochentag, today = self.datum.get_wochentag_datum()
        texts = [wochentag, today]
        fonts = [40, 25]
        x_range, y_range = self.draw_texts(texts, fonts, colors=[BLACK, RED])
        return x_range[1], y_range[1]

    def weather(self):
        y_weather = MARGIN_Y
        temp, icon = self.open_weather.get_weather()
        if temp != "":
            x_range, y_range = self.draw_texts([temp + "°C"], [50], x_aligns=[2])
        else:
            return 0
        y_weather = y_range[1]
        dy = round(y_range[1] - y_range[0])
        icon_size = (dy, dy)
        if icon:
            self.draw_icon(icon, (x_range[0] - icon_size[0], MARGIN_Y), icon_size)
        return y_weather

    def news(self, y):
        titles, descriptions = self.tagesschau.get_news()
        texts = []
        fonts = []
        x_aligns = []
        for t, d in zip(titles, descriptions):
            texts.extend([t, d])
            fonts.extend([25, 20])
            x_aligns.extend([1, 0])
        self.draw_texts(
            texts,
            fonts,
            y_align=2,
            x_aligns=x_aligns,
            y_range=(y, IMAGE_SIZE[1] - MARGIN_Y),
            spacing=10,
        )

    def draw_icon(self, icon, pos, size, color=BLACK):
        pos = (int(pos[0]), int(pos[1]))
        raw_icon = Image.open(os.path.join(PNG_DIR, icon + ".png")).convert("RGBA")
        icon = Image.new("P", raw_icon.size, 0)
        for x in range(raw_icon.size[0]):
            for y in range(raw_icon.size[1]):
                pixel = raw_icon.getpixel((x, y))
                new_color = color
                if pixel[3] < 125:
                    new_color = WHITE
                icon.putpixel((x, y), new_color)
        icon_image = icon.resize(size)
        self.image.paste(icon_image, pos)

    def draw_texts(
        self,
        texts,
        fonts,
        colors=[],
        x_range=(MARGIN_X, IMAGE_SIZE[0] - MARGIN_X),
        y_range=(MARGIN_Y, IMAGE_SIZE[1] - MARGIN_Y),
        y_align=0,  # 0: top, 1: mid, 2: bot
        x_aligns=[],  # 0: left, 1: mid, 2: right
        spacing=0,
    ):
        if y_range[0] > y_range[1]:
            print("Warning: negative space for text")
            return x_range, y_range
        if colors == []:
            colors = [BLACK] * len(texts)
        if x_aligns == []:
            x_aligns = [0] * len(texts)
        all_lines = []
        all_dys = []
        all_dxs = []
        # split into lines and get dxs and dys
        for i in range(len(texts)):
            split = texts[i].split()
            font = self.get_font(fonts[i])
            lines = []
            dxs = []
            dys = []
            while len(split) > 0:
                line = ""
                while (
                    len(split) > 0
                    and self.draw.textsize(line + " " + split[0], font=font)[0]
                    < x_range[1] - x_range[0]
                ):
                    line = line + " " + split[0]
                    del split[0]
                dx, dy = self.draw.textsize(line, font=font)
                lines.append(line)
                dxs.append(dx)
                dys.append(dy)
            all_lines.append(lines)
            all_dxs.append(dxs)
            dys = [max(dys)] * len(dys)  # equal spacing
            all_dys.append(dys)
        for dys in all_dys[:-1]:
            dys[-1] += spacing
        # shorten to fit y_range
        dy_total = sum([a for b in all_dys for a in b])
        while dy_total > y_range[1] - y_range[0]:
            del all_lines[-1]
            del all_dys[-1]
            del all_dxs[-1]
            dy_total = sum([a for b in all_dys for a in b])
        # draw
        y_emtpy = (y_range[1] - y_range[0]) - dy_total
        y_start = y_range[0] + y_emtpy * y_align / 2
        y = y_start
        x_min = x_range[1]
        x_max = x_range[0]
        for i, lines in enumerate(all_lines):
            font = self.get_font(fonts[i])
            for j, line in enumerate(lines):
                x_empty = x_range[1] - x_range[0] - all_dxs[i][j]
                x = x_range[0] + x_empty * x_aligns[i] / 2
                x_min = min(x_min, x)
                x_max = max(x_max, x + all_dxs[i][j])
                self.draw.text((x, y), line, fill=colors[i], font=font)
                y += all_dys[i][j]
        return ((x_min, x_max), (y_start, y))

    def get_font(self, font):
        if font not in fonts:
            fonts[font] = ImageFont.truetype(
                # "/usr/share/fonts/liberation-sans/LiberationSans-%s.ttf" % font[0],
                os.path.join(DIR, "fonts/DejaVuSansCondensed.ttf"),
                # "/usr/share/fonts/paratype-pt-sans/PTS55F.ttf",
                # "fonts/Nintendo-DS-BIOS.ttf",
                # "fonts/Roboto-Regular.ttf",
                size=font,
            )
        return fonts[font]


if __name__ == "__main__":

    d = Drawer()
    img = d.render()
    img.save(os.path.join(DIR, "test.png"))
