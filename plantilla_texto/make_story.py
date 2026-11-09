#!/usr/bin/env python3
"""Instagram story generator for @atleticodigital (reproduces the Picsart template).

Usage:
  python3 make_story.py --headline "TITULAR" --body "Párrafo 1" --body "Párrafo 2" \
      --photo foto1.jpg [--photo foto2.jpg] -o salida.png
  python3 make_story.py --json story.json          # keys: headline, body (list|str), photos (list), output
"""
import argparse, json, os, re, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
TEMPLATE = os.path.join(HERE, "template_bg.png")

# Geometry in pixels of the real template (template_bg.png, 1206x2146), measured from its pixels.
TPL_SIZE = (1206, 2146)
FRAME = (14, 19, 1193, 822)   # inside of the yellow border (x0, y0, x1, y1), photos fill exactly this
LINE_Y = 1099                 # white horizontal line (rows 1098-1101)
HEAD_TOP = 860                # top of the red panel, headline never goes above
HEAD_GAP = 46                 # space between headline baseline and the white line
BODY_TOP = 1165               # cap-top of first body line
BODY_BOTTOM = 1940            # logo starts at y~1985 -> body never goes below this
SIDE = 0.065                  # side margin (fraction of width, each side)

YELLOW = (255, 241, 0)
SHADOW = (40, 0, 0)

HEAD_FONT = os.path.join(FONTS, "AtleticoUCL.ttf")          # 'Atletico de Madrid UCL 2024 - 25'
BODY_FONT = os.path.join(FONTS, "AesthetNova-Bold.ttf")
HEAD_MAX, BODY_MAX = 86, 61   # sizes that match the Picsart example at native template size
# optional extras (only used when --source / --opinion are given)
SOURCE_SCALE, OPINION_SCALE = 0.72, 0.8      # relative to the body size actually used
SOURCE_COLOR = (255, 255, 255)
OPINION_BOX = (0, 0, 0, 225)
# Emoji style. Default: Apple (iPhone) PNGs from npm package emoji-datasource-apple (64px images).
# Missing PNGs fall back to the font list below. Set env STORY_EMOJI_STYLE=font to force fonts.
APPLE_EMOJI_DIR = os.path.join(HERE, "node_modules", "emoji-datasource-apple", "img", "apple", "64")
EMOJI_STYLE = os.environ.get("STORY_EMOJI_STYLE", "apple")
# Emoji font: first existing wins (override with env STORY_EMOJI_FONT). Apple Color Emoji = iPhone look.
EMOJI_CANDIDATES = [os.environ.get("STORY_EMOJI_FONT", ""),
                    os.path.join(FONTS, "AppleColorEmoji.ttc"), os.path.join(FONTS, "AppleColorEmoji.ttf"),
                    os.path.join(FONTS, "NotoColorEmoji.ttf"), "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"]
# bitmap emoji fonts only load at their native strike sizes (Apple sbix: 160/96/64/..., Noto CBDT: 109)
EMOJI_STRIKES = [160, 137, 109, 96, 64, 48, 40, 32]

# Shadows, emulating Picsart "blur 100% / opacity 100%": a dilated, heavily blurred dark halo.
# (spread px, blur radius px, RGBA colour, passes) at native template size
HEAD_SHADOW = (10, 24, (20, 0, 0, 135), 2)
BODY_SHADOW = (4, 14, (30, 0, 0, 105), 1)


# ---------------------------------------------------------------- template
def load_template(path):
    """Use the user's original template exactly. Output at its native size unless it is exactly 9:16,
    in which case it is resized to 1080x1920 (no stretching ever)."""
    if not os.path.exists(path):
        sys.exit(f"Template not found: {path}")
    im = Image.open(path).convert("RGBA")
    if im.width * 16 == im.height * 9 and im.size != (1080, 1920):
        im = im.resize((1080, 1920), Image.LANCZOS)
    return im


# ---------------------------------------------------------------- photos
def sx(v, im): return round(v * im.width / TPL_SIZE[0])
def sy(v, im): return round(v * im.height / TPL_SIZE[1])


def place_photos(im, photos, focus_y=0.2):
    x0, y0, x1, y1 = sx(FRAME[0], im), sy(FRAME[1], im), sx(FRAME[2], im), sy(FRAME[3], im)
    n = len(photos)
    fw = x1 - x0
    for i, p in enumerate(photos):
        a = x0 + fw * i // n
        b = x0 + fw * (i + 1) // n
        ph = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
        ph = ImageOps.fit(ph, (b - a, y1 - y0), Image.LANCZOS, centering=(0.5, focus_y))
        im.paste(ph, (a, y0))


# ---------------------------------------------------------------- text with emoji
EMOJI_RE = re.compile(
    "(?:[\U0001F1E6-\U0001F1FF]{2}|[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u2300-\u23FF]"
    "[\uFE0F\U0001F3FB-\U0001F3FF]*(?:\u200D[\U0001F000-\U0001FAFF\u2600-\u27BF][\uFE0F]*)*)")
_emoji_font = None


def emoji_font():
    """Load the first available colour-emoji font at a size it actually supports."""
    global _emoji_font
    if _emoji_font is None:
        _emoji_font = False
        for path in EMOJI_CANDIDATES:
            if not path or not os.path.exists(path): continue
            for size in EMOJI_STRIKES:
                try:
                    f = ImageFont.truetype(path, size, index=0)
                    t = Image.new("RGBA", (size * 2, size * 2))
                    ImageDraw.Draw(t).text((size, size), "\U0001F600", font=f, embedded_color=True, anchor="mm")
                    if t.getbbox():
                        _emoji_font = f
                        print(f"[emoji] {os.path.basename(path)} @ {size}", file=sys.stderr)
                        break
                except Exception:
                    continue
            if _emoji_font: break
    return _emoji_font


def runs(text):
    out, pos = [], 0
    for m in EMOJI_RE.finditer(text):
        if m.start() > pos: out.append((False, text[pos:m.start()]))
        out.append((True, m.group()))
        pos = m.end()
    if pos < len(text): out.append((False, text[pos:]))
    # strip emojis gracefully if neither an Apple PNG nor a colour font can draw them
    out = [r for r in out if not r[0] or apple_png(r[1]) or emoji_font()]
    return out


def apple_png(e):
    """Map an emoji sequence to its Apple PNG (lowercase hex joined by '-'), with/without fe0f."""
    if EMOJI_STYLE != "apple" or not os.path.isdir(APPLE_EMOJI_DIR): return None
    cps = [f"{ord(c):x}" for c in e]
    stripped = [c for c in cps if c != "fe0f"]
    cands = ["-".join(cps), "-".join(stripped)]
    if stripped: cands.append("-".join([stripped[0], "fe0f"] + stripped[1:]))
    for c in cands:
        p = os.path.join(APPLE_EMOJI_DIR, c + ".png")
        if os.path.exists(p): return p
    return None


def emoji_img(e, size):
    p = apple_png(e)
    if p:
        img = Image.open(p).convert("RGBA")
        return img.resize((size, size), Image.LANCZOS)
    ef = emoji_font()
    if not ef: return None
    n = ef.size * 2
    tmp = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((n // 2, n // 2), e, font=ef, embedded_color=True, anchor="mm")
    bb = tmp.getbbox()
    if not bb: return None
    tmp = tmp.crop(bb)
    s = size / max(tmp.size)
    return tmp.resize((max(1, int(tmp.width * s)), max(1, int(tmp.height * s))), Image.LANCZOS)


def text_width(s, font):
    w = 0
    for is_e, t in runs(s):
        w += font.size * 1.1 if is_e else font.getlength(t)
    return w


def wrap(text, font, maxw):
    lines, cur = [], ""
    for word in text.split():
        cand = (cur + " " + word).strip()
        if text_width(cand, font) <= maxw or not cur:
            cur = cand
        else:
            lines.append(cur); cur = word
    if cur: lines.append(cur)
    return lines


def balance(text, font, maxw):
    """Wrap, then shrink the width so lines are visually balanced (Picsart-like)."""
    lines = wrap(text, font, maxw)
    if len(lines) < 2: return lines
    w = maxw
    while w > maxw * 0.5:
        t = wrap(text, font, w - 10)
        if len(t) > len(lines): break
        w -= 10; lines = t
    return lines


def line_runs(s, font, cx, base):
    """Yield (is_emoji, text, x) positions for a centred line."""
    x = cx - text_width(s, font) / 2
    for is_e, t in runs(s):
        yield is_e, t, x
        x += font.size * 1.1 if is_e else font.getlength(t)


def draw_halo(im, lines, shadow, k):
    """Soft Picsart-style shadow behind a block of lines: [(text, font, cx, base), ...]."""
    spread, blur, col, passes = shadow
    spread, blur = max(1, round(spread * k)), max(1, round(blur * k))
    mask = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(mask)
    for s, font, cx, base in lines:
        cap = -font.getbbox("H", anchor="ls")[1]
        for is_e, t, x in line_runs(s, font, cx, base):
            if is_e:
                r = font.size * 0.45
                ex, ey = x + font.size * 0.1 + r, base - cap * 0.5
                d.ellipse([ex - r - spread, ey - r - spread, ex + r + spread, ey + r + spread], fill=255)
            else:
                d.text((x, base), t, font=font, fill=255, anchor="ls", stroke_width=spread, stroke_fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    mask = mask.point(lambda v: min(255, int(v * col[3] / 255)))
    layer = Image.new("RGBA", im.size, col[:3] + (0,))
    layer.putalpha(mask)
    for _ in range(passes):
        im.alpha_composite(layer)


def draw_line(im, s, font, cx, base, fill):
    """Draw one centred line on baseline `base`; handles emoji runs."""
    cap = font.getbbox("H", anchor="ls")[1]  # negative: cap height above baseline
    d = ImageDraw.Draw(im)
    for is_e, t, x in line_runs(s, font, cx, base):
        if is_e:
            em = emoji_img(t, int(font.size * 0.9))
            if em:
                im.paste(em, (int(x + font.size * 0.1), int(base + cap * 0.5 - em.height / 2 + font.size * 0.02)), em)
        else:
            d.text((x, base), t, font=font, fill=fill, anchor="ls")


# ---------------------------------------------------------------- main render
def head_font(size): return ImageFont.truetype(HEAD_FONT, size)
def body_font(size): return ImageFont.truetype(BODY_FONT, size)


def render(headline, body, photos, output, template=None, focus_y=0.2,
           source=None, opinion=None, keep_lines=False, reserve_bottom=0):
    """Optional (all off by default, so default output is unchanged):
    source         -> small source line under the body (e.g. '🗞️ Vía @marca')
    opinion        -> author's opinion in a black rounded box under the source
    keep_lines     -> keep single line breaks inside a paragraph (lists like a XI) without blank lines
    reserve_bottom -> px (native template scale) kept free above the logo, e.g. for an IG poll sticker"""
    im = load_template(template or TEMPLATE)
    W = im.width
    k = im.width / TPL_SIZE[0]          # scale factor for sizes if template resized
    if photos: place_photos(im, photos, focus_y)
    maxw = W * (1 - 2 * SIDE)
    cx = W / 2
    ly = sy(LINE_Y, im)

    # headline: bottom line's baseline sits HEAD_GAP above the white line
    headline = headline.upper()
    base_last = ly - round(HEAD_GAP * k)
    zone_top = sy(HEAD_TOP, im)
    for size in range(round(HEAD_MAX * k), 20, -2):
        hf = head_font(size)
        hl = balance(headline, hf, maxw)
        lh = round(size * 0.98)
        cap = -hf.getbbox("H", anchor="ls")[1]
        top = base_last - (len(hl) - 1) * lh - cap
        if len(hl) <= 3 and top >= zone_top and all(text_width(l, hf) <= maxw for l in hl):
            break
    base0 = base_last - (len(hl) - 1) * lh
    draw_halo(im, [(l, hf, cx, base0 + i * lh) for i, l in enumerate(hl)], HEAD_SHADOW, k)
    for i, l in enumerate(hl):
        draw_line(im, l, hf, cx, base0 + i * lh, YELLOW)

    # body: paragraphs separated by a blank line, auto-shrinks so it never reaches the logo
    if isinstance(body, str): body = body.split("\n\n")
    paras = [p.strip() for p in body if p.strip()]
    top, bot = sy(BODY_TOP, im), sy(BODY_BOTTOM - (reserve_bottom or 0), im)

    def wrap_para(p, f):
        if not keep_lines: return wrap(p, f, maxw)
        return [l for sub in p.split("\n") if sub.strip() for l in wrap(sub.strip(), f, maxw)]

    for size in range(round(BODY_MAX * k), 16, -1):
        bf = body_font(size)
        lh = round(size * 1.2)
        gap = lh                         # one blank line between paragraphs
        cap = -bf.getbbox("H", anchor="ls")[1]
        desc = bf.getmetrics()[1]
        wrapped = [wrap_para(p, bf) for p in paras]
        n = sum(len(w) for w in wrapped)
        total = cap + (n - 1) * lh + gap * (len(wrapped) - 1) + desc
        extra = 0
        if source:
            sf = body_font(max(14, round(size * SOURCE_SCALE)))
            s_lh = round(sf.size * 1.2)
            s_lines = wrap(source, sf, maxw)
            s_cap = -sf.getbbox("H", anchor="ls")[1]
            extra += round(lh * 0.7) + s_cap + (len(s_lines) - 1) * s_lh + sf.getmetrics()[1]
        if opinion:
            of = body_font(max(14, round(size * OPINION_SCALE)))
            o_lh = round(of.size * 1.2)
            o_pad = round(of.size * 0.6)
            o_lines = wrap(opinion, of, maxw - 2 * o_pad)
            o_cap = -of.getbbox("H", anchor="ls")[1]
            o_h = 2 * o_pad + o_cap + (len(o_lines) - 1) * o_lh + of.getmetrics()[1]
            extra += round(lh * 0.7) + o_h
        if total + extra <= bot - top: break
    placed, base = [], top + cap
    for wl in wrapped:
        for l in wl:
            placed.append((l, bf, cx, base))
            base += lh
        base += gap
    draw_halo(im, placed, BODY_SHADOW, k)
    for l, f, x, b in placed:
        draw_line(im, l, f, x, b, (255, 255, 255))
    y_end = (placed[-1][3] if placed else top) + desc

    if source:
        sp, b = [], y_end + round(lh * 0.7) + s_cap
        for l in s_lines:
            sp.append((l, sf, cx, b)); b += s_lh
        draw_halo(im, sp, BODY_SHADOW, k)
        for l, f, x, bb in sp:
            draw_line(im, l, f, x, bb, SOURCE_COLOR)
        y_end = sp[-1][3] + sf.getmetrics()[1]

    if opinion:
        bw = max(text_width(l, of) for l in o_lines) + 2 * o_pad
        bx0, by0 = cx - bw / 2, y_end + round(lh * 0.7)
        box = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle([bx0, by0, bx0 + bw, by0 + o_h], radius=round(o_pad * 0.8),
                                              fill=OPINION_BOX)
        im.alpha_composite(box)
        b = by0 + o_pad + o_cap
        for l in o_lines:
            draw_line(im, l, of, cx, b, (255, 255, 255)); b += o_lh
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    im.convert("RGB").save(output)
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json")
    ap.add_argument("--headline")
    ap.add_argument("--body", action="append", help="one paragraph (repeatable)")
    ap.add_argument("--photo", action="append", help="1 or 2 photos")
    ap.add_argument("--template", help="background (default: template_bg.png next to script)")
    ap.add_argument("--focus-y", type=float, default=0.2, help="vertical crop focus 0=top 1=bottom")
    ap.add_argument("-o", "--output", default="story.png")
    ap.add_argument("--source", help="optional small source line under the body")
    ap.add_argument("--opinion", help="optional opinion text in a black box")
    ap.add_argument("--keep-lines", action="store_true", help="keep single line breaks inside paragraphs")
    ap.add_argument("--reserve-bottom", type=int, default=0, help="px kept free above the logo (sticker)")
    a = ap.parse_args()
    if a.json:
        with open(a.json, encoding="utf-8") as f: j = json.load(f)
        headline, body = j["headline"], j.get("body", [])
        photos = j.get("photos", []); out = j.get("output", a.output)
        tpl = j.get("template", a.template); fy = j.get("focus_y", a.focus_y)
        extra = dict(source=j.get("source", a.source), opinion=j.get("opinion", a.opinion),
                     keep_lines=j.get("keep_lines", a.keep_lines),
                     reserve_bottom=j.get("reserve_bottom", a.reserve_bottom))
    else:
        if not a.headline: ap.error("--headline or --json required")
        headline, body, photos, out, tpl, fy = a.headline, a.body or [], a.photo or [], a.output, a.template, a.focus_y
        extra = dict(source=a.source, opinion=a.opinion, keep_lines=a.keep_lines, reserve_bottom=a.reserve_bottom)
    if len(photos) > 2: ap.error("max 2 photos")
    print(render(headline, body, photos, out, tpl, fy, **extra))


if __name__ == "__main__":
    main()
