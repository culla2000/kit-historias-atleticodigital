# plantilla_historias_2 — historia "normal" (foto + texto blanco)

Para alternar con la plantilla roja (plantilla_historias_1): ~1 de esa por cada 2 de estas.
Se lee en 2 segundos: titular corto + 1–2 líneas + fuente.

## Uso
    python3 make_story2.py historia.json [otra.json ...]

## JSON
```json
{
  "headline": "EL CUTI SE PIERDE AL BARÇA",          // corto, SF Pro Display Heavy ~96 px (baja solo hasta caber en 2 líneas)
  "body": ["Lesión muscular. Tampoco irá con Argentina."], // opcional; 1–3 líneas (un pelín más si hace falta para entenderse sin contexto; no rellenar). Cada elemento = un párrafo, SF Pro Medium 46 px
  "source": "Vía @marca",                               // SF Pro Regular 28 px, blanco 70 %
  "photo": "/ruta/foto.jpg",                           // ideal vertical o grande (>1300 px de alto)
  "focus_y": 0.3,                                      // 0 = arriba, 1 = abajo (recorte cover a 1080x1920)
  "text_position": "bottom",                           // bottom | top
  "output": "/ruta/salida.jpg"
}
```
Opcionales: `focus_x` (0 = izquierda, 1 = derecha, por defecto 0.5), `headline_size`, `body_size`, `logo`.

## Diseño
- 1080x1920, foto a pantalla completa, degradado negro suave solo detrás del texto.
- Zonas libres: arriba 250 px (barra de IG); abajo 170 px (caja de respuesta). Con texto abajo,
  el centro de la foto queda libre para el comentario/stickers de Cristóbal; con texto arriba, el hueco es la mitad baja.
- Logo AD de 104 px en la esquina derecha (arriba, justo debajo de los 250 px de la barra, si el texto va abajo; abajo si va arriba).
- Texto alineado a la izquierda, ancho máximo (márgenes 64 px), evita dejar una palabra sola en la última línea.
- Emojis estilo iPhone (PNG de Apple de plantilla_historias_1/node_modules). Usarlos con moderación.

## Fotos (feedback Cristóbal)
- Alta resolución: el script avisa (AVISO en stderr) si tiene que ampliar la foto más de un 5 %. Ideal: alto ≥ 1920 px
  (o ancho ≥ 1080 px y alto ≥ 1920 px tras el recorte). En X, descargar con `?name=orig`.
- Planos amplios: cuerpo entero, la jugada o la escena. Nunca primeros planos de solo la cara.
- Encuadra con `focus_x`/`focus_y` para que el texto no tape al jugador (texto abajo → jugador en la mitad superior/central).

## Estilos (campo "style")
Campos extra: `tag` (píldora de categoría: "Lesión", "Última hora", "Mercado"…), `dorsal` (para el estilo dorsal).
- `clasico`: foto + degradado negro + texto. Sin píldora.
- `rayas`: rayas rojiblancas diagonales difuminadas que nacen del degradado inferior; píldora roja #CB3524; @atleticodigital vertical en el borde.
- `cristal`: panel de cristal esmerilado estilo iOS (blur de la propia foto, esquinas redondeadas, borde fino) detrás del texto; píldora amarilla #FFE014.
- `dorsal`: número de dorsal gigante rojo semitransparente con contorno blanco detrás del texto (abajo a la derecha); píldora roja; @atleticodigital vertical.
- `grano`: duotono parcial marino→rojo + trama halftone y grano en la zona del texto; píldora amarilla.
- `marco` (**POR DEFECTO**, elegido por Cristóbal el 05/11/2026): marco fino blanco redondeado, barra amarilla junto al titular, firma rojiblanca en el borde inferior, @atleticodigital vertical colocado SOBRE la línea derecha del marco (la línea se corta a su altura, pegado al borde) y logo AD a 8 px de la línea interior del marco (`MARCO_GAP`); píldora roja.
Ejemplo: `{"style": "cristal", "tag": "Lesión", ...}`. Copia de la versión anterior: make_story2.py.bak_v3.

Si no se pone `style`, se usa `marco`. Para la foto+degradado sin adornos: `"style": "clasico"`. Copia previa al cambio: make_story2.py.bak_estilos.

## Emoji grande (OPCIONAL, NO sale por defecto)
Solo se dibuja si el JSON trae `emoji`. Uso excepcional, cuando venga muy al caso (feedback Cristóbal 05/11/2026).
**Regla: emojis SIEMPRE en estilo iOS (Apple). Nunca Noto ni Google.**
Campos: `emoji` (carácter, p. ej. "✅"), `emoji_x` / `emoji_y` (centro, en fracción 0–1 del ancho/alto; por defecto 0.78 / 0.45),
`emoji_size` (px, recomendado 180–240; por defecto 220), `emoji_rotate` (grados, por defecto -8; 0 = recto).
Imagen: PNG de Apple de 160 px (el tamaño máximo que trae la fuente Apple Color Emoji) del repositorio iamcal/emoji-data
(`img-apple-160/<codepoint>.png`), descargado una vez y guardado en `emoji_cache/apple/`. Se reescala con Lanczos (×1,4 a 220 px, se ve nítido).
Si no se encuentra la versión de Apple, el script escribe un AVISO y NO dibuja el emoji (no cae a Noto).
Sombra suave. Colócalo en un hueco (cielo, césped, grada), sin tapar caras ni el texto, fuera de los 250 px de arriba / 170 px de abajo.
Los emojis pequeños dentro del texto también son de Apple (emoji-datasource-apple, 64 px).

## Marco: posición de la marca (05/11/2026)
Logo AD arriba a la derecha pegado a la zona segura (y = 250, `LOGO_Y_MARCO`) y a 8 px de la línea del marco.
@atleticodigital vertical sobre la línea derecha del marco, empezando justo debajo del logo (≈ y 400–600, tercio superior).
Copia previa: make_story2.py.bak_marco_v1. Antes del cambio a emojis de Apple: make_story2.py.bak_noto.

## Collage (varias fotos)
En vez de `photo`, pasa `photos`: lista de rutas o de objetos `{"path": ..., "focus_x": 0.5, "focus_y": 0.3}`.
- `layout`: `"columns"` (franjas verticales, por defecto: perfecto para 2–3 fotos verticales de cuerpo entero) o `"rows"` (franjas horizontales).
- `gap`: separación en px (por defecto 6); `gap_color`: color RGB (por defecto blanco [255,255,255]).
Cada foto se recorta tipo "cover" a su franja; avisa si alguna se amplía más de un 5 %. `photo` sigue funcionando igual.
Copia previa: make_story2.py.bak_photo1.
