# Kit de historias — @atleticodigital

Kit para generar historias de Instagram de la cuenta de aficionados **@atleticodigital** (Atlético de Madrid).
Pensado para que Muse (u otra herramienta) pueda reproducir el mismo estilo.

Hay **dos plantillas**. Proporción habitual: **~1 historia de plantilla de texto por cada 2 historias “normales” (marco)**.

---

## Requisitos

```bash
python3 -m pip install -r requirements.txt
# Pillow >= 10
```

Opcional (emojis Apple en plantilla de texto):

```bash
cd plantilla_texto && npm i emoji-datasource-apple
```

Si no instalas el paquete npm, la plantilla de texto usa `fonts/NotoColorEmoji.ttf` como fallback.
La plantilla marco descarga emojis Apple a `emoji_cache/apple/` solo si el JSON pide un emoji grande.

---

## 1) Plantilla marco (la habitual)

Carpeta: `plantilla_marco/` · script: `make_story2.py` · salida: **1080×1920**.

```bash
cd ejemplos/02_liderato
python3 ../../plantilla_marco/make_story2.py historia.json
# genera resultado_regen.jpg
```

### Campos del JSON

| Campo | Obligatorio | Notas |
|-------|-------------|--------|
| `style` | no | Por defecto `"marco"`. Otros: `clasico`, `rayas`, `cristal`, `dorsal`, `grano` |
| `tag` | recomendado | Píldora roja: `"LaLiga"`, `"Mercado"`, `"Selección"`… |
| `headline` | sí | Titular corto, máx. ~2 líneas |
| `body` | no | Lista de párrafos (1–2 suele bastar) |
| `source` | recomendado | p. ej. `"Vía @Atleti"` |
| `photo` | sí* | Ruta a la foto (*o `photos` para collage) |
| `focus_x` / `focus_y` | no | Recorte cover (0–1). Por defecto 0.5 / 0.3 |
| `text_position` | no | `"bottom"` (habitual) o `"top"` |
| `output` | sí | Ruta del JPG/PNG de salida |
| `emoji` | no | Solo excepcional; emoji grande estilo Apple |

Ejemplo mínimo:

```json
{
  "style": "marco",
  "tag": "LaLiga",
  "headline": "TITULAR CORTO",
  "body": ["Una o dos frases claras."],
  "source": "Vía @Atleti",
  "photo": "foto.jpg",
  "focus_x": 0.5,
  "focus_y": 0.3,
  "text_position": "bottom",
  "output": "salida.jpg"
}
```

Detalle extra: `plantilla_marco/LEEME.md`.

---

## 2) Plantilla de texto (roja / Picsart)

Carpeta: `plantilla_texto/` · script: `make_story.py` · fondo: `template_bg.png`.

```bash
cd ejemplos/05_barrios_plantilla1
python3 ../../plantilla_texto/make_story.py --json historia.json
```

JSON: `headline`, `body` (lista), `photos` (1–2), `output`; opcionales `focus_y`, `source`, `keep_lines`, `reserve_bottom`.

Detalle: `plantilla_texto/README.md`.

---

## Reglas de estilo (obligatorias)

1. **Foto a pantalla completa**, alta calidad y alta resolución. Plano amplio: cuerpo entero, jugada o escena. **Nunca** un primer plano solo de la cara.
2. **Nunca el estadio vacío a solas.** Mejor jugadores en acción o entrenando.
3. **Texto blanco corto** en SF Pro, con jerarquía de tamaño y peso, rápido de leer. Añadir un poco más solo si hace falta para entender la noticia.
4. **Sin emoji grande por defecto**; solo excepcionalmente.
5. Los emojis van **siempre en estilo Apple iOS**.
6. **Logo Atlético Digital** arriba, pegado al borde (la plantilla marco ya lo coloca).
7. **@atleticodigital** en vertical sobre la línea derecha del marco.
8. **Nunca** 😂 ni emojis de burla hacia el Atleti o su afición.

---

## Fuentes de noticias y fotos

- Fotos oficiales: cuenta **@Atleti** en X. Descargar desde `pbs.twimg.com` con `?name=orig` (máxima resolución).
- Rumores / filtraciones: marcar como **sin confirmar** en el texto o en la fuente.
- No inventar titulares; ceñirse a lo publicado.

---

## Flujo para ahorrar (importante)

1. **Primero el texto** (tag, titular, body, source) y la **foto** propuesta → revisar y aprobar.
2. **Solo entonces** generar el diseño, **una sola vez**.
3. Retoques de foto (`focus_x` / `focus_y`) solo si hace falta.

Así se evita regenerar la historia varias veces.

---

## Contenido del kit

```
GUIA.md
requirements.txt
plantilla_marco/     make_story2.py, logo_ad.png, fonts/ (SF Pro Display), emoji_cache/, LEEME.md
plantilla_texto/     make_story.py, template_bg.png, fonts/, package.json, README.md
ejemplos/
  01_convocatoria/   historia.json + foto.jpg + resultado.jpg   (marco)
  02_liderato/       …                                           (marco)
  03_matchday/       …                                           (marco)
  04_horarios/       …                                           (marco)
  05_barrios_plantilla1/ …                                       (plantilla texto)
```

---

## Aviso legal — tipografías

- **SF Pro** (Apple): obtenida de developer.apple.com/fonts. **Apple no permite redistribuirla libremente.** En este kit se incluyen solo los pesos Display necesarios para que Muse pueda probar. Para un uso serio, Muse debe instalar SF Pro desde Apple o sustituirla por una alternativa con licencia clara (Inter, etc.) sabiendo que el look cambiará.
- **AtleticoUCL** / **AesthetNova**: tipografías del proyecto; no están pensadas para redistribución pública fuera del equipo.
- Fotos de ejemplo: material de apoyo del club / usos de aficionado; no son un banco libre de derechos.

---

## Qué no incluye este kit

Contraseñas, tokens, cookies ni datos de acceso a Instagram/X. Solo plantillas, scripts, assets y ejemplos.

- NotoColorEmoji.ttf se ha quitado del kit (no es el estilo Apple). Instala emoji-datasource-apple con npm para los emojis.
