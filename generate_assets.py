"""Generate image assets for DineSight. Run once to create assets/."""

import os

from PIL import Image, ImageDraw, ImageFont

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS, exist_ok=True)


def _font(size):
    for name in ["segoeuib.ttf", "segoeui.ttf", "arial.ttf", "arialbd.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _emoji_font(size):
    for name in ["seguiemj.ttf", "NotoColorEmoji.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return _font(size)


def rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def make_category_icon(filename, bg_color, emoji, label):
    size = 120
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rounded_rect(draw, (0, 0, size - 1, size - 1), 20, bg_color)
    ef = _font(36)
    draw.text((size // 2, 38), emoji, fill="#ffffff", font=ef, anchor="mm")
    lf = _font(13)
    draw.text((size // 2, 82), label, fill="#ffffff", font=lf, anchor="mm")
    img.save(os.path.join(ASSETS, filename))


def make_dashboard_banner():
    w, h = 800, 160
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Gradient-like banner
    for y in range(h):
        r = int(37 + (y / h) * 10)
        g = int(99 + (y / h) * 20)
        b = int(235 - (y / h) * 30)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
    # Round corners
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, w - 1, h - 1), radius=16, fill=255)
    img.putalpha(mask)
    # Text
    tf = _font(28)
    sf = _font(14)
    draw = ImageDraw.Draw(img)
    draw.text((40, 45), "Welcome to DineSight", fill="#ffffff", font=tf)
    draw.text((40, 90), "Your restaurant command center", fill="#c7d2fe", font=sf)
    # Decorative circles
    for cx, cy, rad in [(680, 40, 30), (720, 100, 20), (750, 50, 15)]:
        draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(255, 255, 255, 30))
    img.save(os.path.join(ASSETS, "dashboard_banner.png"))


def make_pos_icon():
    size = 80
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rounded_rect(draw, (0, 0, size - 1, size - 1), 16, "#2563eb")
    f = _font(32)
    draw.text((size // 2, size // 2 - 2), "POS", fill="#ffffff", font=f, anchor="mm")
    img.save(os.path.join(ASSETS, "pos_icon.png"))


def make_quick_sale_icon():
    size = 48
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Green circle with +
    draw.ellipse((0, 0, size - 1, size - 1), fill="#059669")
    f = _font(28)
    draw.text((size // 2, size // 2 - 2), "+", fill="#ffffff", font=f, anchor="mm")
    img.save(os.path.join(ASSETS, "quick_sale.png"))


def make_stat_icons():
    icons = [
        ("revenue_icon.png", "#2563eb", "$"),
        ("orders_icon.png", "#059669", "#"),
        ("monthly_icon.png", "#7c3aed", "M"),
        ("top_item_icon.png", "#d97706", "\u2605"),
    ]
    for filename, color, symbol in icons:
        size = 44
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=12, fill=color)
        f = _font(20)
        draw.text(
            (size // 2, size // 2 - 1), symbol, fill="#ffffff", font=f, anchor="mm"
        )
        img.save(os.path.join(ASSETS, filename))


def make_empty_plate():
    """A simple plate illustration for empty states."""
    size = 200
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Plate
    draw.ellipse((20, 40, 180, 180), fill="#e2e8f0", outline="#cbd5e1", width=2)
    draw.ellipse((50, 60, 150, 150), fill="#f1f5f9", outline="#e2e8f0", width=1)
    # Fork/knife
    draw.line((60, 20, 60, 50), fill="#94a3b8", width=3)
    draw.line((55, 20, 65, 20), fill="#94a3b8", width=2)
    draw.line((140, 20, 140, 50), fill="#94a3b8", width=3)
    f = _font(14)
    draw.text((size // 2, 110), "No data yet", fill="#94a3b8", font=f, anchor="mm")
    img.save(os.path.join(ASSETS, "empty_plate.png"))


if __name__ == "__main__":
    print("Generating DineSight assets...")
    categories = [
        ("cat_appetizer.png", "#f59e0b", "AP", "Appetizer"),
        ("cat_main.png", "#ef4444", "MC", "Main Course"),
        ("cat_dessert.png", "#ec4899", "DS", "Dessert"),
        ("cat_beverage.png", "#3b82f6", "BV", "Beverage"),
        ("cat_special.png", "#8b5cf6", "SP", "Special"),
    ]
    for fname, color, emoji, label in categories:
        make_category_icon(fname, color, emoji, label)
        print(f"  {fname}")

    make_dashboard_banner()
    print("  dashboard_banner.png")

    make_pos_icon()
    print("  pos_icon.png")

    make_quick_sale_icon()
    print("  quick_sale.png")

    make_stat_icons()
    print("  stat icons")

    make_empty_plate()
    print("  empty_plate.png")

    print("Done! Assets saved to:", ASSETS)
