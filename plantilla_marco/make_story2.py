#!/usr/bin/env python3
"""Historia 'normal' @atleticodigital: foto a pantalla completa + texto blanco SF Pro. Ver LEEME.md"""
import json, sys, os, argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
# Rutas relativas al kit (portables). Orden: fonts/ del kit, luego rutas legacy del box.
_FONT_CANDIDATES = [
    os.path.join(HERE, 'fonts'),
    '/workspace/plantillas/plantilla_tipo1_cita/San-Francisco-Pro-Fonts-master',
]
FONTS = next((d for d in _FONT_CANDIDATES if os.path.isdir(d)), _FONT_CANDIDATES[0])
_EMOJI_CANDIDATES = [
    os.path.join(HERE, 'emoji_cache', 'apple'),
    os.path.join(HERE, 'node_modules', 'emoji-datasource-apple', 'img', 'apple', '64'),
    os.path.join(HERE, '..', 'plantilla_texto', 'node_modules', 'emoji-datasource-apple', 'img', 'apple', '64'),
    '/workspace/plantillas/plantilla_historias_1/node_modules/emoji-datasource-apple/img/apple/64',
]
EMOJI_DIR = next((d for d in _EMOJI_CANDIDATES if os.path.isdir(d)), _EMOJI_CANDIDATES[0])
W, H = 1080, 1920
SAFE_TOP = 250          # barra de Instagram
SAFE_BOTTOM = 170       # caja "Enviar mensaje"
MARGIN_X = 64
LOGO = 104
F = lambda n, s: ImageFont.truetype(os.path.join(FONTS, n), s)

def cover(img, fy, fx=0.5):
    img = img.convert('RGB'); s = max(W / img.width, H / img.height)
    if s > 1.05:
        print(f'AVISO: la foto se amplía x{s:.2f} ({img.width}x{img.height}); busca una de más resolución', file=sys.stderr)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = round((img.width - W) * fx); y = round((img.height - H) * fy)
    return img.crop((x, y, x + W, y + H))

def emoji_png(ch):
    cps = [f'{ord(c):04x}' for c in ch]
    for c in ('-'.join(cps), '-'.join(x for x in cps if x != 'fe0f')):
        p = os.path.join(EMOJI_DIR, c + '.png')
        if os.path.exists(p): return Image.open(p).convert('RGBA')
    return None

def is_emoji(c): return ord(c) >= 0x2190 and not (0x2000 <= ord(c) < 0x2190)

def tokens(word):
    """divide palabra en trozos texto/emoji"""
    out, i = [], 0
    while i < len(word):
        c = word[i]
        if is_emoji(c):
            j = i + 1
            while j < len(word) and (word[j] in '\ufe0f\u200d' or (word[j-1] == '\u200d') or 0x1F3FB <= ord(word[j]) <= 0x1F3FF or 0x1F1E6 <= ord(c) <= 0x1F1FF and j == i+1 and 0x1F1E6 <= ord(word[j]) <= 0x1F1FF):
                j += 1
            out.append(('e', word[i:j])); i = j
        else:
            j = i
            while j < len(word) and not is_emoji(word[j]): j += 1
            out.append(('t', word[i:j])); i = j
    return out

def wwidth(word, font):
    return sum(font.size * 1.05 if k == 'e' else font.getlength(s) for k, s in tokens(word))

def wrap(text, font, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if wwidth(t, font) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    # evita viuda (una palabra sola en la última línea)
    if len(lines) > 1 and len(lines[-1].split()) == 1:
        prev = lines[-2].split()
        if len(prev) > 2 and wwidth(prev[-1] + ' ' + lines[-1], font) <= maxw:
            lines[-2] = ' '.join(prev[:-1]); lines[-1] = prev[-1] + ' ' + lines[-1]
    return lines

def draw_line(txt_layer, sh_layer, x, y, line, font, fill):
    d, ds = ImageDraw.Draw(txt_layer), ImageDraw.Draw(sh_layer)
    asc = font.getmetrics()[0]
    words = line.split(' ')
    for wi, w in enumerate(words):
        for k, s in tokens(w):
            if k == 't':
                ds.text((x, y), s, font=font, fill=(0, 0, 0, 170)); d.text((x, y), s, font=font, fill=fill)
                x += font.getlength(s)
            else:
                e = emoji_png(s); sz = round(font.size * 0.95)
                if e:
                    e = e.resize((sz, sz), Image.LANCZOS)
                    txt_layer.alpha_composite(e, (round(x), round(y + asc - sz * 0.88)))
                x += font.size * 1.05
        if wi < len(words) - 1: x += font.getlength(' ')

RED = (203, 53, 36); YEL = (255, 224, 20); NAVY = (39, 46, 97)
FRAME_M = 26; MARCO_GAP = 8; LOGO_Y_MARCO = SAFE_TOP   # marco: margen del marco y separación de logo/@ respecto a su línea interior
STYLES = ('clasico', 'rayas', 'cristal', 'dorsal', 'grano', 'marco')

def rounded_mask(size, r):
    m = Image.new('L', size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0]-1, size[1]-1), r, fill=255); return m

def stripes(w, h, band=90, angle=0):
    im = Image.new('RGB', (w, h), (255, 255, 255)); d = ImageDraw.Draw(im)
    for x in range(-h, w + h, band * 2):
        if angle: d.polygon([(x, h), (x + band, h), (x + band + h, 0), (x + h, 0)], fill=RED)
        else: d.rectangle((x, 0, x + band - 1, h), fill=RED)
    return im

def grad_mask(y0, y1, a0, a1, power=1.0):
    g = Image.new('L', (1, H), 0)
    for yy in range(H):
        t = 0 if yy < y0 else 1 if yy > y1 else (yy - y0) / max(1, y1 - y0)
        g.putpixel((0, yy), int(a0 + (a1 - a0) * (t ** power)) if y0 <= yy else int(a0) if a0 and False else (0 if yy < y0 else int(a1)))
    return g.resize((W, H))

def pill(layer, x, y, text, bg, fg):
    f = F('SF-Pro-Display-Bold.otf', 30); tw = f.getlength(text); ph = 52; pw = round(tw + 44)
    d = ImageDraw.Draw(layer); d.rounded_rectangle((x, y, x + pw, y + ph), ph // 2, fill=bg + (255,))
    d.text((x + 22, y + ph / 2), text, font=f, fill=fg, anchor='lm'); return ph

def halftone(w, h, cell=14, color=(255, 255, 255), alpha_top=0, alpha_bot=70):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for yy in range(0, h, cell):
        t = yy / max(1, h); r = cell * 0.5 * (0.15 + 0.8 * t)
        for xx in range((yy // cell % 2) * cell // 2, w, cell):
            d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=color + (int(alpha_top + (alpha_bot - alpha_top) * t),))
    return im

EMOJI_CACHE = os.path.join(HERE, 'emoji_cache')
NOTO_TTF = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'

APPLE_CACHE = os.path.join(EMOJI_CACHE, 'apple')
APPLE_URLS = ['https://raw.githubusercontent.com/iamcal/emoji-data/master/img-apple-160/{c}.png',
              'https://cdn.jsdelivr.net/gh/iamcal/emoji-data@master/img-apple-160/{c}.png']

def big_emoji_img(ch, size):
    """Emoji grande SIEMPRE estilo Apple iOS: PNG de 160 px (el máximo que publica Apple en su fuente)
    de iamcal/emoji-data (img-apple-160), cacheado en emoji_cache/apple/. Si no existe, avisa y devuelve None (nunca Noto)."""
    cps = [f'{ord(c):x}' for c in ch]
    cands = ['-'.join(cps), '-'.join(c for c in cps if c != 'fe0f')]
    os.makedirs(APPLE_CACHE, exist_ok=True)
    path = None
    for c in cands:
        pth = os.path.join(APPLE_CACHE, c + '.png')
        if os.path.exists(pth): path = pth; break
    if not path:
        import urllib.request
        for c in cands:
            for u in APPLE_URLS:
                try:
                    b = urllib.request.urlopen(urllib.request.Request(u.format(c=c), headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read()
                    pth = os.path.join(APPLE_CACHE, c + '.png'); open(pth, 'wb').write(b); path = pth; break
                except Exception:
                    continue
            if path: break
    if not path:
        print(f'AVISO: no encuentro el emoji de Apple para {ch!r} ({cands[0]}); NO se dibuja (no se usa Noto).', file=sys.stderr)
        return None
    im = Image.open(path).convert('RGBA')
    im = im.crop(im.getchannel('A').getbbox())
    r = size / max(im.size)
    if r > 1.6: print(f'AVISO: emoji {ch!r} ampliado x{r:.2f} desde 160 px; mejor emoji_size <= 250', file=sys.stderr)
    return im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)

def paste_big_emoji(out, cfg):
    ch = cfg.get('emoji')
    if not ch: return out
    size = int(cfg.get('emoji_size', 220)); rot = float(cfg.get('emoji_rotate', -8))
    e = big_emoji_img(ch, size)
    if e is None: return out
    if rot: e = e.rotate(rot, resample=Image.BICUBIC, expand=True)
    cx, cy = float(cfg.get('emoji_x', 0.78)) * W, float(cfg.get('emoji_y', 0.45)) * H
    x, y = round(cx - e.width / 2), round(cy - e.height / 2)
    # sombra suave
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); a = e.getchannel('A').point(lambda v: v * 0.55)
    blk = Image.new('RGBA', e.size, (0, 0, 0, 255)); blk.putalpha(a); sh.alpha_composite(blk, (x + 6, y + 14))
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(14)))
    out.alpha_composite(e, (x, y))
    return out

def cover_to(img, w, h, fy=0.3, fx=0.5, label=''):
    img = img.convert('RGB'); sc = max(w / img.width, h / img.height)
    if sc > 1.05:
        print(f'AVISO: {label} se amplía x{sc:.2f} ({img.width}x{img.height}); busca una de más resolución', file=sys.stderr)
    img = img.resize((round(img.width * sc), round(img.height * sc)), Image.LANCZOS)
    x = round((img.width - w) * fx); y = round((img.height - h) * fy)
    return img.crop((x, y, x + w, y + h))

def build_background(cfg):
    """Una foto (`photo`) o collage (`photos`: lista de rutas o de {"path","focus_x","focus_y"}).
    `layout`: "columns" (franjas verticales, por defecto; ideal para fotos verticales de cuerpo entero) o "rows".
    `gap` px de separación (por defecto 6), color `gap_color` (por defecto blanco)."""
    photos = cfg.get('photos')
    if not photos:
        return cover(Image.open(cfg['photo']), float(cfg.get('focus_y', 0.3)), float(cfg.get('focus_x', 0.5)))
    items = [p if isinstance(p, dict) else {'path': p} for p in photos]
    n = len(items); gap = int(cfg.get('gap', 6)); layout = cfg.get('layout', 'columns')
    canvas = Image.new('RGB', (W, H), tuple(cfg.get('gap_color', (255, 255, 255))))
    total = (W if layout == 'columns' else H) - gap * (n - 1)
    pos = 0
    for k, it in enumerate(items):
        size = total // n + (1 if k < total % n else 0)
        w, h = (size, H) if layout == 'columns' else (W, size)
        tile = cover_to(Image.open(it['path']), w, h, float(it.get('focus_y', 0.3)), float(it.get('focus_x', 0.5)), os.path.basename(it['path']))
        canvas.paste(tile, (pos, 0) if layout == 'columns' else (0, pos))
        pos += size + gap
    return canvas

def render(cfg):
    style = cfg.get('style', 'marco')
    if style not in STYLES: raise SystemExit(f'style desconocido: {style} ({", ".join(STYLES)})')
    pos = cfg.get('text_position', 'bottom')
    bg = build_background(cfg).convert('RGBA')
    photo = bg.copy()
    mx = MARGIN_X + (36 if style == 'cristal' else 0) + (20 if style == 'marco' else 0)
    maxw = W - 2 * mx
    hs = int(cfg.get('headline_size', 96))
    while True:
        hf = F('SF-Pro-Display-Heavy.otf', hs); hl = wrap(cfg['headline'], hf, maxw)
        if len(hl) <= 2 or hs <= 66: break
        hs -= 4
    bf = F('SF-Pro-Display-Medium.otf', int(cfg.get('body_size', 46)))
    sf = F('SF-Pro-Display-Regular.otf', 28)
    body = cfg.get('body') or []
    if isinstance(body, str): body = [body]
    PARA_GAP = 14
    bl = []
    for pi, p_ in enumerate(body):
        for li, l in enumerate(wrap(p_, bf, maxw)): bl.append((l, pi > 0 and li == 0))
    hlh, blh = round(hs * 1.08), round(bf.size * 1.28)
    tag = cfg.get('tag') if style != 'clasico' else None
    tagh = 52 + 26 if tag else 0
    block = tagh + len(hl) * hlh + (28 + len(bl) * blh + PARA_GAP * sum(g for _, g in bl) if bl else 0) + 34 + 34
    bottom_limit = H - SAFE_BOTTOM - (30 if style == 'cristal' else 0)
    y0 = SAFE_TOP + 10 + (30 if style == 'cristal' else 0) if pos == 'top' else bottom_limit - block

    # ---- fondo según estilo ----
    pad = 260
    dark = 205 if style in ('clasico', 'dorsal', 'marco') else 150 if style == 'cristal' else 185
    g = Image.new('L', (1, H), 0)
    for yy in range(H):
        t = (yy - (y0 - pad)) / (block + pad) if pos == 'bottom' else ((y0 + block + pad) - yy) / (block + pad)
        t = max(0.0, min(1.0, t)); g.putpixel((0, yy), int(dark * (t ** 1.4)))
    gmask = g.resize((W, H))
    if style == 'grano':   # duotono parcial rojo-marino en la zona del texto
        gray = photo.convert('L')
        duo = Image.merge('RGB', [gray.point(lambda v: int(NAVY[i] + (RED[i] - NAVY[i]) * v / 255 * 0.9)) for i in range(3)]).convert('RGBA')
        bg = Image.composite(duo, bg, gmask.point(lambda v: min(255, int(v * 1.25))))
    shade = Image.new('RGBA', (W, H), (0, 0, 0, 255)); shade.putalpha(gmask)
    bg = Image.alpha_composite(bg, shade)
    if style == 'rayas':   # rayas rojiblancas difuminadas que nacen del degradado
        st = stripes(W, H, band=64, angle=1).filter(ImageFilter.GaussianBlur(12)).convert('RGBA')
        m = gmask.point(lambda v: int(v * 0.5))
        st.putalpha(m); bg = Image.alpha_composite(bg, st)
        shade2 = Image.new('RGBA', (W, H), (0, 0, 0, 255)); shade2.putalpha(gmask.point(lambda v: int(v * 0.55)))
        bg = Image.alpha_composite(bg, shade2)
    if style == 'grano':
        ht = halftone(W, H - max(0, y0 - pad), cell=12, alpha_top=0, alpha_bot=38)
        top = y0 - pad if pos == 'bottom' else 0
        bg.alpha_composite(ht, (0, max(0, top)))
        import random; random.seed(7)
        noise = Image.effect_noise((W, H), 40).convert('L').point(lambda v: v)
        nl = Image.new('RGBA', (W, H), (255, 255, 255, 0)); nl.putalpha(Image.composite(noise.point(lambda v: int(v * 0.12)), Image.new('L', (W, H), 0), gmask))
        bg = Image.alpha_composite(bg, nl)
    if style == 'dorsal' and cfg.get('dorsal'):
        nf = F('SF-Pro-Display-Black.otf', 900)
        num = Image.new('RGBA', (W, H), (0, 0, 0, 0)); nd = ImageDraw.Draw(num)
        nf = F('SF-Pro-Display-Black.otf', 620)
        nd.text((W + 30, y0 + block + 40), str(cfg['dorsal']), font=nf, anchor='rb', fill=RED + (95,), stroke_width=4, stroke_fill=(255, 255, 255, 110))
        bg = Image.alpha_composite(bg, num)
    if style == 'cristal':   # panel de cristal esmerilado estilo iOS
        px0, px1 = MARGIN_X - 14, W - MARGIN_X + 14
        py0, py1 = y0 - 40, y0 + block + 6
        blur = photo.filter(ImageFilter.GaussianBlur(38)).crop((px0, py0, px1, py1))
        tint = Image.new('RGBA', blur.size, (20, 20, 24, 110)); glass = Image.alpha_composite(blur, tint)
        hl_ = Image.new('RGBA', blur.size, (255, 255, 255, 0)); ImageDraw.Draw(hl_).rounded_rectangle((0, 0, blur.size[0]-1, blur.size[1]-1), 44, outline=(255, 255, 255, 70), width=2)
        glass = Image.alpha_composite(glass, hl_)
        sh_ = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh_).rounded_rectangle((px0, py0 + 14, px1, py1 + 14), 44, fill=(0, 0, 0, 120))
        bg = Image.alpha_composite(bg, sh_.filter(ImageFilter.GaussianBlur(24)))
        bg.paste(glass, (px0, py0), rounded_mask(glass.size, 44))

    # ---- texto ----
    txt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    y = y0
    if tag:
        colors = {'rayas': (RED, (255, 255, 255)), 'cristal': (YEL, (20, 20, 20)), 'dorsal': (RED, (255, 255, 255)), 'grano': (YEL, (20, 20, 20)), 'marco': (RED, (255, 255, 255))}[style]
        pill(txt, mx, y, tag.upper(), *colors); y += tagh
    if style == 'marco':
        ImageDraw.Draw(txt).rectangle((mx - 26, y + 8, mx - 17, y + len(hl) * hlh - 8), fill=YEL + (255,))
    for l in hl: draw_line(txt, sh, mx, y, l, hf, (255, 255, 255, 255)); y += hlh
    if bl:
        y += 28
        for l, gap in bl:
            if gap: y += PARA_GAP
            draw_line(txt, sh, mx, y, l, bf, (255, 255, 255, 240)); y += blh
    y += 34
    if cfg.get('source'): draw_line(txt, sh, mx, y, cfg['source'], sf, (255, 255, 255, 175))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    if style == 'cristal': sh = sh.point(lambda v: v // 2) if False else sh
    out = Image.alpha_composite(Image.alpha_composite(bg, sh), txt)

    out = paste_big_emoji(out, cfg)
    # ---- marca de la casa ----
    lab = None
    if style in ('marco', 'dorsal', 'rayas'):
        hf2 = F('SF-Pro-Display-Semibold.otf', 24)
        handle = '@atleticodigital'
        tw = round(hf2.getlength(handle)) + 4
        lab = Image.new('RGBA', (tw, 34), (0, 0, 0, 0)); ImageDraw.Draw(lab).text((0, 2), handle, font=hf2, fill=(255, 255, 255, 170 if style != 'marco' else 215))
        lab = lab.rotate(90, expand=True)
        bb = lab.getchannel('A').getbbox()
        lab_y = SAFE_TOP + 560 if style != 'marco' else LOGO_Y_MARCO + LOGO + 50
        if style != 'marco':
            out.alpha_composite(lab, (W - 52, lab_y))
    if style == 'marco':
        m = FRAME_M
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(fr)
        d.rounded_rectangle((m, m, W - m, H - m), 36, outline=(255, 255, 255, 150), width=3)
        d.line((m + 60, H - m, m + 260, H - m), fill=RED + (255,), width=7)
        d.line((m + 260, H - m, m + 460, H - m), fill=(255, 255, 255, 255), width=7)
        # el @ va SOBRE la línea derecha del marco, que se interrumpe a su altura (centrado en la línea)
        line_cx = W - m - 1
        lab_x = line_cx - (bb[0] + bb[2]) // 2
        ImageDraw.Draw(fr).rectangle((W - m - 6, lab_y + bb[1] - MARCO_GAP - 6, W - m + 3, lab_y + bb[3] + MARCO_GAP + 6), fill=(0, 0, 0, 0))
        out = Image.alpha_composite(out, fr)
        out.alpha_composite(lab, (lab_x, lab_y))
    logo = Image.open(cfg.get('logo', os.path.join(HERE, 'logo_ad.png'))).convert('RGBA').resize((LOGO, LOGO), Image.LANCZOS)
    lx = (W - FRAME_M - 3 - MARCO_GAP - LOGO) if style == 'marco' else W - LOGO - 40
    ly = (LOGO_Y_MARCO if style == 'marco' else SAFE_TOP + 6) if pos == 'bottom' else H - SAFE_BOTTOM - LOGO + 20
    out.alpha_composite(logo, (lx, ly))
    o = cfg['output']; os.makedirs(os.path.dirname(o) or '.', exist_ok=True)
    out = out.convert('RGB')
    if o.lower().endswith(('.jpg', '.jpeg')): out.save(o, quality=93)
    else: out.save(o)
    print(o)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('json', nargs='+'); a = ap.parse_args()
    for j in a.json: render(json.load(open(j)))
