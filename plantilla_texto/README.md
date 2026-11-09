# @atleticodigital – generador de stories

Usa la plantilla original de Picsart **tal cual** (`template_bg.png`, 1206x2146) y solo coloca encima:
foto(s) dentro del marco amarillo, titular amarillo (fuente `AtleticoUCL.ttf`, sombra oscura) justo encima
de la línea blanca, y cuerpo blanco (`AesthetNova-Bold.ttf`) centrado debajo, sin tocar el logo.

## Uso
```bash
cd /workspace/stories
python3 make_story.py --headline "GRIEZMANN DESPEJA LAS DUDAS: ÉL SÍ SE QUEDA" \
  --body "Primer párrafo 😍" --body "Segundo párrafo 🏆" \
  --photo foto1.jpg [--photo foto2.jpg] -o salida.png
# o con JSON
python3 make_story.py --json test_griezmann.json
```
JSON: `headline`, `body` (lista de párrafos, o texto con párrafos separados por línea en blanco),
`photos` (1 o 2), `output`; opcionales `template`, `focus_y`.

## Detalles
- Salida a tamaño nativo de la plantilla (1206x2146, no es exactamente 9:16, así que no se estira).
  Si se usa una plantilla exactamente 9:16 se exporta a 1080x1920.
- Marco de fotos (interior del borde amarillo): x 14–1193, y 19–822. 2 fotos = izquierda/derecha, recorte "cover".
  `--focus-y` (0 = arriba, 1 = abajo, por defecto 0.2) elige qué parte vertical de la foto se conserva.
- Línea blanca en y=1099; titular con su última línea a 46 px por encima; cuerpo de y=1165 a y=1940
  (el logo empieza en y≈1985).
- Tamaños por defecto: titular 86 px (se reduce y reparte en 1–3 líneas equilibradas), cuerpo 61 px con
  interlineado 1.2 y una línea en blanco entre párrafos; se reduce solo si no cabe.
- Sombras estilo Picsart (blur/opacity 100%): halo oscuro muy difuminado, sin contorno. Ajustables en
  `HEAD_SHADOW` / `BODY_SHADOW` (expansión px, radio de blur px, color RGBA, pasadas).
- Emojis estilo iPhone (por defecto): PNG de Apple del paquete npm `emoji-datasource-apple`
  (`node_modules/emoji-datasource-apple/img/apple/64/<unified>.png`, 64 px, el mayor disponible). Instalar con
  `cd /workspace/stories && npm i emoji-datasource-apple`. Si falta un PNG se usa una fuente de color
  (`$STORY_EMOJI_FONT`, `fonts/AppleColorEmoji.ttc/.ttf` o Noto Color Emoji); si no hay nada, se elimina.
  `STORY_EMOJI_STYLE=font` fuerza el uso de fuente.
- Si falta `template_bg.png` el script se detiene con error (ya no dibuja ninguna plantilla de reserva).
