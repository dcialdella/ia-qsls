#!/usr/bin/env python3
"""
Generador de Postales QSL desde archivos ADI (ADIF)
Usa a1.png/a2.png como fondos y superpone los datos de contacto.

Lógica inteligente:
  - Cada carpeta qslN tiene su log (qslN/qsl_log.json).
  - Solo se procesan los ADI nuevos o modificados.
  - Si un PNG ya generado falta, se regenera solo ese.
  - Los PNG ya generados no se repiten.

Estructura:
  qsl1-qsl7/          -> cada carpeta = una actividad
    *.adi             -> archivo ADIF con los contactos
    *.png (fondo)     -> imagen de fondo para las postales
    QSLS/             -> postales generadas
    qsl_log.json      -> log de procesado (se crea automáticamente)
"""

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Versión del generador: si un ADI ya registrado en el log se generó con otra
# versión, se reprocesa (permite que cambios de código se reflejen al ejecutar
# en modo incremental sin necesidad de --from-scratch).
GENERATOR_VERSION = "2"

# Estación propia que se muestra en la esquina inferior derecha de cada postal
STATION_TEXT = "EG9MM - Melilla"

# Rangos de banda (MHz) para derivar BAND desde FREQ (evita reconstruir la lista)
BAND_RANGES = [
    ('2190m', 0.135, 0.137), ('630m', 0.472, 0.479),
    ('160m', 1.8, 2.0), ('80m', 3.5, 4.0), ('60m', 5.3, 5.4),
    ('40m', 7.0, 7.3), ('30m', 10.0, 10.15), ('20m', 14.0, 14.35),
    ('17m', 18.068, 18.168), ('15m', 21.0, 21.45),
    ('12m', 24.89, 24.99), ('10m', 28.0, 29.7),
    ('6m', 50.0, 54.0), ('4m', 70.0, 70.5), ('2m', 144.0, 148.0),
    ('70cm', 432.0, 438.0), ('23cm', 1240.0, 1300.0),
]


class ADIFParser:
    """Parser robusto para archivos ADI/ADIF.

    Soporta:
      - Tags con/ sin longitud y tipo: <CALL:5>, <CALL:5:S>, <CALL>
      - Encodings UTF-8 (con o sin BOM) y cp1252/latin-1 (SmartLogger Windows)
      - Cabeceras ADIF (<ADIF_VER>, <PROGRAMID>, <EOH>, <USERDEF>...)
      - Programas que exportan <DX_CALL> en vez de <CALL> (buses FT8/FT4)
      - Tags malformados sin romper el procesado del resto del archivo
    """

    # Campos propios de la cabecera/gestión, nunca datos de QSO
    HEADER_KEYS = {
        'ADIF_VER', 'ADIFVER', 'PROGRAMID', 'PROGRAM_NAME', 'PROGRAMVERSION',
        'EOH', 'USERDEF', 'CREATED_TIMESTAMP', 'GENERATED_TIMESTAMP',
        'LASTUPDATED', 'SUBMITTED', 'ENDOFLOG', 'APP_ADIF_VER',
    }

    @staticmethod
    def _read_text(filepath):
        """Lee el archivo tolerando BOM, UTF-8 y cp1252/latin-1."""
        raw = Path(filepath).read_bytes()
        if raw.startswith(b'\xef\xbb\xbf'):
            raw = raw[3:]
        try:
            return raw.decode('utf-8')
        except UnicodeDecodeError:
            return raw.decode('cp1252', errors='replace')

    @staticmethod
    def parse(filepath):
        """Parsea un archivo ADIF y retorna una lista de contactos (QSOs)."""
        content = ADIFParser._read_text(filepath)
        pattern = re.compile(r'<(\w+)(?::(\d+)(?::\w+)?)?>', re.IGNORECASE)
        tags = [
            (m.start(), m.group(1), int(m.group(2)) if m.group(2) else 0)
            for m in pattern.finditer(content)
        ]

        qsos = []
        current_qso = {}
        for idx, (pos, tag, length) in enumerate(tags):
            tag_upper = tag.upper()
            if tag_upper == 'EOR':  # Fin de registro
                clean = ADIFParser._resolve_call(current_qso)
                if clean:
                    qsos.append(clean)
                current_qso = {}
                continue
            if tag_upper in ADIFParser.HEADER_KEYS:
                continue

            close = content.find('>', pos)
            if close < 0:  # < malformado: ignorar y seguir
                continue
            raw_start = close + 1
            raw_end = tags[idx + 1][0] if idx + 1 < len(tags) else len(content)
            raw = content[raw_start:raw_end]
            if length and length > 0:
                raw = raw[:length]
            # strip() recorta SOLO los extremos; los espacios internos
            # (p.ej. QTH "san fernando") se conservan íntegros.
            value = raw.strip()
            # Nunca sobrescribir la llamada con una vacía
            if tag_upper == 'CALL' and not value:
                continue
            current_qso[tag_upper] = value

        return qsos

    @staticmethod
    def _resolve_call(qso):
        """Resuelve el callsign del contacto. Prioriza CALL y acepta DX_CALL.

        Devuelve None (y descarta el registro) si no hay llamada: evita
        postales 'unknown' por cabeceras o registros vacíos.
        """
        call = (qso.get('CALL') or qso.get('DX_CALL') or '').strip().upper()
        if not call:
            return None
        qso['CALL'] = call
        return qso


class QSLGenerator:
    """Genera postales QSL usando una imagen de fondo + datos de contacto"""

    # Tamaño de postal (proporción 3:2)
    WIDTH = 1200
    HEIGHT = 800

    def __init__(self):
        self.fonts = {}
        self._flag_img = None
        self._flag_tile = None      # bandera ya redimensionada (5% x 5% de la postal)
        self._bg_cache = {}         # path -> RGBA ya escalado a 'cover' (evita reescalar 5000x)
        self._flag_text_cache = {}  # (texto, tamaño fuente) -> imagen RGBA lista para pegar
        self._station_flag_cache = {}  # (iso2, alto) -> imagen RGBA pequeña de bandera
        self._country_map = None    # country_map.json cargado bajo demanda (lazy)

    def prepare_background(self, path):
        """Devuelve la imagen de fondo ya escalada a 'cover' y RGBA (cacheada).

        En ~5000 postales el fondo se reutiliza mucho: se prepara una sola vez
        por archivo en lugar de reabrir/reescalar en cada postal.
        """
        key = str(path)
        if key not in self._bg_cache:
            with Image.open(path) as bg:
                prepped = self.cover_fit(bg, self.WIDTH, self.HEIGHT).convert('RGBA')
            self._bg_cache[key] = prepped
        return self._bg_cache[key]

    def get_flag_image(self):
        """Carga la bandera de España desde FLAGS/es.png (cacheado).

        Si no existe, devuelve None y el renderizado cae al dibujo por franjas.
        """
        if self._flag_img is None:
            path = Path(__file__).with_name('FLAGS') / 'es.png'
            if path.exists():
                try:
                    self._flag_img = Image.open(path).convert('RGBA')
                except Exception:
                    self._flag_img = None
        return self._flag_img

    def _load_country_map(self):
        """Carga country_map.json (prefijos -> ISO2) una sola vez.

        Devuelve un dict {primera_letra: [items...]} con cada lista ordenada
        por longitud de prefijo DESCENDENTE (más específico primero), para
        resolver el país en O(prefijos de esa letra) en lugar de O(todos).
        """
        if self._country_map is None:
            path = Path(__file__).with_name('country_map.json')
            items = []
            if path.exists():
                try:
                    with open(path, encoding='utf-8') as f:
                        items = json.load(f)
                except Exception:
                    items = []
            index = {}
            for it in items:
                if not isinstance(it, dict):
                    continue
                p = it.get('p')
                if not isinstance(p, str) or not p:
                    continue
                index.setdefault(p[0], []).append(it)
            for lst in index.values():
                lst.sort(key=QSLGenerator._country_sort_key)
            self._country_map = index
        return self._country_map

    @staticmethod
    def _country_sort_key(item):
        """Clave de orden segura: ignora ítems con 'ent' no numérico."""
        try:
            ent = int(item.get('ent'))
        except (TypeError, ValueError):
            ent = 0
        return (-len(item['p']), ent)

    def country_code_for_call(self, call):
        """Deriva el código ISO2 del país desde el prefijo del callsign.

        Busca solo entre los prefijos que empiezan por la primera letra
        de la llamada (ya ordenados por especificidad descendente).
        Devuelve None para placeholders (N/A, UNKNOWN) y llamadas con
        caracteres no válidos, para no asociar bandera errónea.
        """
        call = (call or '').upper().strip()
        if not call or call in ('N/A', 'UNKNOWN', 'WW', 'CALL') \
                or re.search(r'[^A-Z0-9/]', call):
            return None
        for item in self._load_country_map().get(call[0], []):
            if call.startswith(item['p']):
                return item['cc']
        return None

    def station_flag(self, call, height):
        """Devuelve la bandera del país de `call` redimensionada a `height` px de alto.

        Resultado cacheado por (iso2, alto). None si no se puede determinar
        el país o no existe su bandera en FLAGS/.
        """
        cc = self.country_code_for_call(call)
        if not cc:
            return None
        key = (cc, height)
        if key not in self._station_flag_cache:
            img = None
            path = Path(__file__).with_name('FLAGS') / f"{cc.lower()}.png"
            if path.exists():
                try:
                    with Image.open(path) as raw:
                        raw = raw.convert('RGBA')
                    ratio = height / raw.height
                    new_w = max(1, round(raw.width * ratio))
                    img = raw.resize((new_w, height), Image.LANCZOS)
                except Exception:
                    img = None
            self._station_flag_cache[key] = img
        return self._station_flag_cache[key]

    def get_font(self, size, bold=False):
        """Obtiene una fuente del sistema (cacheada)"""
        key = (size, bold)
        if key not in self.fonts:
            candidates = [
                '/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf',
                '/System/Library/Fonts/Helvetica.ttc',
                '/System/Library/Fonts/Supplemental/Verdana Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Verdana.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            ]
            for path in candidates:
                if os.path.exists(path):
                    try:
                        self.fonts[key] = ImageFont.truetype(path, size)
                        break
                    except Exception:
                        continue
            else:
                self.fonts[key] = ImageFont.load_default()
        return self.fonts[key]

    @staticmethod
    def cover_fit(bg, target_w, target_h):
        """Escala la imagen de fondo a 'cover' (recorte centrado al ratio objetivo)"""
        src_w, src_h = bg.size
        target_ratio = target_w / target_h
        src_ratio = src_w / src_h

        if src_ratio > target_ratio:
            # Imagen más ancha -> recortar los lados
            new_w = int(src_h * target_ratio)
            left = (src_w - new_w) // 2
            bg = bg.crop((left, 0, left + new_w, src_h))
        else:
            # Imagen más alta -> recortar arriba/abajo
            new_h = int(src_w / target_ratio)
            top = (src_h - new_h) // 2
            bg = bg.crop((0, top, src_w, top + new_h))

        return bg.resize((target_w, target_h), Image.LANCZOS)

    @staticmethod
    def rounded_rect(draw, xy, radius, fill):
        x0, y0, x1, y1 = xy
        r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
        draw.rounded_rectangle(xy, radius=r, fill=fill)

    def draw_activity_checkboxes(self, draw, box, checked, pad_x=24, pad_y=10,
                                 n=6, cw=30, ch=30, spacing=6,
                                 act_label="ACT", flag_box=None):
        """Dibuja la fila de casillas QSL1..QSL6 con un rótulo a la izquierda.

        `checked`: set de índices 1-based de actividades tildadas.
        `flag_box`: índice 1-based de una casilla donde se dibuja la bandera
        de España en lugar de un tilde (None = ninguna).
        """
        cb_bottom = box[3] - pad_y - 4
        cb_y = cb_bottom - ch

        font_act = self.get_font(20, bold=True)
        bbox_act = draw.textbbox((0, 0), act_label, font=font_act)
        act_w = bbox_act[2] - bbox_act[0]

        total_w = act_w + 10 + n * cw + (n - 1) * spacing
        # Alineado a la derecha de la caja (mismo margen interior que el texto)
        start_x = box[2] - total_w - pad_x
        act_x = start_x
        boxes_x = [act_x + act_w + 10 + i * (cw + spacing) for i in range(n)]

        check = (245, 166, 35, 255)  # dorado
        rojo = (198, 11, 30, 255)
        amarillo = (255, 200, 0, 255)
        font_num = self.get_font(20, bold=True)
        for i in range(n):
            x0 = int(boxes_x[i])
            y0 = cb_y
            # Cuadro de la casilla (más chico)
            draw.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=7,
                                   outline=(255, 255, 255, 230), width=2)
            if flag_box == i + 1:
                # Bandera de España dentro de la casilla (rojo-amarillo-rojo 1:2:1)
                bx0, by0 = x0 + 3, y0 + 2
                bw, bh = cw - 6, ch - 4
                third_y = by0 + bh / 4
                draw.rectangle([bx0, by0, bx0 + bw, third_y], fill=rojo)
                draw.rectangle([bx0, third_y, bx0 + bw, by0 + bh - bh / 4], fill=amarillo)
                draw.rectangle([bx0, by0 + bh - bh / 4, bx0 + bw, by0 + bh], fill=rojo)
            elif (i + 1) in checked:
                # Til reemplaza el número si la actividad está lograda
                cx0, cy0 = x0 + 6, y0 + ch * 0.52
                cx1, cy1 = x0 + cw * 0.42, y0 + ch - 6
                cx2, cy2 = x0 + cw - 5, y0 + 7
                draw.line([(cx0, cy0), (cx1, cy1)], fill=check, width=4, joint="curve")
                draw.line([(cx1, cy1), (cx2, cy2)], fill=check, width=4, joint="curve")
            else:
                # Número de la actividad dentro de la casilla
                num = str(i + 1)
                bbox = draw.textbbox((0, 0), num, font=font_num)
                nw = bbox[2] - bbox[0]
                draw.text((x0 + (cw - nw) / 2, y0 + ch / 2 - 1), num,
                          font=font_num, fill=(255, 255, 255, 230), anchor="lm")

        # Rótulo "ACT" a la izquierda de la fila
        draw.text((int(act_x), cb_y + ch / 2), act_label,
                  font=font_act, fill=(255, 255, 255, 235), anchor="lm")

    def draw_spanish_flag(self, draw, margin=10):
        """Dibuja la bandera de España en la esquina superior derecha.

        Usa FLAGS/es.png si existe; si no, dibuja las franjas 1:2:1 como
        fallback. Tamaño 5% x 5% de la postal.
        """
        fw = int(self.WIDTH * 0.05)
        fh = int(self.HEIGHT * 0.05)
        bx0 = self.WIDTH - fw - margin
        by0 = margin
        bx1, by1 = bx0 + fw, by0 + fh
        flag = self.get_flag_image()
        if flag is not None:
            if self._flag_tile is None:
                self._flag_tile = flag.resize((fw, fh), Image.LANCZOS)
            # Necesitamos pegar sobre la misma imagen que usa `draw`
            draw._image.paste(self._flag_tile.convert('RGB'), (bx0, by0))
        else:
            self._draw_spanish_flag_rects(draw, bx0, by0, bx1, by1, fh)
        draw.rectangle([bx0, by0, bx1, by1], outline=(0, 0, 0, 255), width=2)

    @staticmethod
    def _draw_spanish_flag_rects(draw, bx0, by0, bx1, by1, fh):
        """Banderita por franjas (fallback si no existe FLAGS/es.png)."""
        rojo = (198, 11, 30, 255)
        amarillo = (255, 200, 0, 255)
        third_y = by0 + fh / 4
        draw.rectangle([bx0, by0, bx1, third_y], fill=rojo)
        draw.rectangle([bx0, third_y, bx1, by1 - fh / 4], fill=amarillo)
        draw.rectangle([bx0, by1 - fh / 4, bx1, by1], fill=rojo)

    def draw_flag_color_text(self, overlay, pos, text, font):
        """Dibuja `text` con la silueta coloreada como la bandera de España:
        franja superior e inferior rojas y centro amarillo (1:2:1).

        `pos` = (x, y) con y = centro vertical del texto (anchor "lm").
        Recorta los colores usando una máscara del glifo y solo trabaja sobre
        el bounding box del texto (no sobre toda la postal de 1200x800).
        """
        key = (text, font.size, pos)
        if key not in self._flag_text_cache:
            mask = Image.new('L', (self.WIDTH, self.HEIGHT), 0)
            ImageDraw.Draw(mask).text(pos, text, font=font, fill=255, anchor="lm")
            bb = mask.getbbox()
            if not bb:
                return
            x0, y0, x1, y1 = bb
            th = y1 - y0
            sep = th / 4
            rojo = (198, 11, 30, 255)
            amarillo = (255, 200, 0, 255)
            # Capa del tamaño del bbox, no de toda la postal
            flag = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
            fd = ImageDraw.Draw(flag)
            fd.rectangle([0, 0, x1 - x0, sep], fill=rojo)
            fd.rectangle([0, sep, x1 - x0, th - sep], fill=amarillo)
            fd.rectangle([0, th - sep, x1 - x0, th], fill=rojo)
            flag.putalpha(mask.crop(bb))
            self._flag_text_cache[key] = (flag, (x0, y0))
        flag, (x0, y0) = self._flag_text_cache[key]
        overlay.alpha_composite(flag, dest=(x0, y0))

    @staticmethod
    def fmt_date(qso):
        """Formatea QSO_DATE a DD/MM/AAAA tolerando YYYYMMDD o YYYY-MM-DD."""
        d = (qso.get('QSO_DATE') or '').strip()
        digits = re.sub(r'\D', '', d)
        if len(digits) == 8:
            return f"{digits[6:8]}/{digits[4:6]}/{digits[0:4]}"
        return d or '----'

    @staticmethod
    def fmt_time(qso):
        """Formatea TIME_ON a HH:MM:SS UTC tolerando HHMMSS o HH:MM:SS."""
        t = (qso.get('TIME_ON') or '').strip()
        digits = re.sub(r'\D', '', t)
        if len(digits) < 4:
            return t
        hh, mm = digits[0:2], digits[2:4]
        ss = digits[4:6] if len(digits) >= 6 else '00'
        return f"{hh}:{mm}:{ss} UTC"

    @staticmethod
    def band_from_freq(freq):
        """Deriva la banda a partir de la frecuencia (MHz) si falta BAND."""
        try:
            f = float(freq)
        except (TypeError, ValueError):
            return ''
        for name, lo, hi in BAND_RANGES:
            if lo <= f <= hi:
                return name
        return ''

    def draw_station_flag(self, overlay, call, x, center_y, height):
        """Dibuja la bandera del país de `call` delante del nombre.

        Devuelve la coordenada x donde debe empezar el texto (después de la
        bandera más un pequeño margen). Si no hay bandera, devuelve `x` intacto.
        """
        flag = self.station_flag(call, height)
        if flag is None:
            return x
        overlay.alpha_composite(flag, dest=(x, center_y - height // 2))
        return x + flag.width + 6

    def compose(self, background_path, qso, activity=None):
        """Compone una postal con la info del contacto sobre el fondo.

        Los datos van en una caja en la esquina inferior izquierda.
        Debajo de los datos, una fila de casillas QSL1..QSL6 con tilde en la
        actividad que corresponde (parámetro `activity`, 1-based; None = ninguna).
        """
        img = self.prepare_background(background_path)
        overlay = Image.new('RGBA', (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Caja de datos: 22% alto (17% + 5% para que entre el texto), 55% ancho
        box_h = int(self.HEIGHT * 0.22)
        box_w = int(self.WIDTH * 0.55)
        pad_x = 24
        pad_y = 10
        box = [25, self.HEIGHT - box_h - 25, 25 + box_w, self.HEIGHT - 25]
        self.rounded_rect(draw, box, 16, (0, 0, 0, 150))
        # Borde sutil de la caja
        draw.rounded_rectangle(box, radius=16, outline=(255, 255, 255, 90), width=2)

        # Bandera de España, esquina superior derecha (5% x 5%)
        self.draw_spanish_flag(draw)

        # ===== Datos del contacto =====
        date_str = self.fmt_date(qso)
        time_str = self.fmt_time(qso)

        call = qso.get('CALL', 'N/A')
        band = qso.get('BAND', '') or self.band_from_freq(qso.get('FREQ', ''))
        mode = qso.get('MODE', '')
        name = qso.get('NAME', qso.get('OPERATOR', ''))
        qth = qso.get('QTH', '')
        grid = qso.get('GRIDSQUARE', '')

        # Líneas de contenido en la zona superior de la caja
        inner_top = box[1] + pad_y + 12
        line_h = 24

        font_call = self.get_font(26, bold=True)
        font_data = self.get_font(18)
        font_info = self.get_font(16)

        # Línea 1: Callsign
        draw.text((box[0] + pad_x, inner_top), call,
                  font=font_call, fill=(255, 255, 255, 255), anchor="lm")

        # Esquina inferior derecha: operador de la estación, en colores de bandera,
        # dentro de una minicaja con contraste (igual estilo que la caja de datos)
        station_text = STATION_TEXT
        font_station = self.get_font(52, bold=True)
        sbox = draw.textbbox((0, 0), station_text, font=font_station)
        sw, sh = sbox[2] - sbox[0], sbox[3] - sbox[1]
        spx, spy = 16, 10
        sxy = [self.WIDTH - 25 - sw - spx * 2,
               self.HEIGHT - 25 - sh - spy * 2,
               self.WIDTH - 25,
               self.HEIGHT - 25]
        self.rounded_rect(draw, sxy, 12, (0, 0, 0, 150))
        draw.rounded_rectangle(sxy, radius=12, outline=(255, 255, 255, 90), width=2)
        self.draw_flag_color_text(overlay, (sxy[0] + spx, sxy[1] + spy + sh / 2),
                                  station_text, font_station)

        # Línea 2: Fecha + hora
        draw.text((box[0] + pad_x, inner_top + line_h * 1), f"{date_str}  {time_str or '--:--'}",
                  font=font_data, fill=(255, 255, 255, 240), anchor="lm")

        # Línea 3: Banda + modo
        if band or mode:
            band_mode = " / ".join(x for x in [band, mode] if x)
            draw.text((box[0] + pad_x, inner_top + line_h * 2), band_mode,
                      font=font_data, fill=(255, 255, 255, 240), anchor="lm")

        # Línea 4: nombre / qth / grid / tu callsign (con bandera del país delante)
        info = "  •  ".join(x for x in [name, qth, grid] if x)
        if info:
            y_info = inner_top + line_h * 3
            fh = font_info.size
            x_name = box[0] + pad_x
            x_name = self.draw_station_flag(overlay, call, x_name, y_info, fh)
            draw.text((x_name, y_info), info,
                      font=font_info, fill=(255, 255, 255, 230), anchor="lm")

        # Casillas de actividades (tilde en la que corresponde)
        # Actividad 7 (DMR): en lugar de casillas, texto de confirmación
        if activity == 7:
            font_dmr = self.get_font(20, bold=True)
            dmr_text = "DMR Confirmated"
            bbox = draw.textbbox((0, 0), dmr_text, font=font_dmr)
            tw = bbox[2] - bbox[0]
            draw.text((box[2] - pad_x - tw, box[3] - pad_y - 12), dmr_text,
                      font=font_dmr, fill=(255, 255, 255, 235), anchor="lm")
        else:
            checked = {activity} if activity and 1 <= activity <= 6 else set()
            self.draw_activity_checkboxes(draw, box, checked, pad_x=pad_x, act_label="ACT",
                                          n=6, cw=26, ch=26, spacing=6)

        # Componer
        result = Image.alpha_composite(img, overlay).convert('RGB')
        return result

    def compose_act6(self, background_path, call, name, grid):
        """Compone la postal de Actividad 6: reconoce a una estación que
        contactó en TODAS las actividades.

        Muestra: callsign, nombre, grid locator y las casillas QSL1..QSL6
        con tilde en las 5 actividades logradas (QSL1..QSL5).
        """
        img = self.prepare_background(background_path)
        overlay = Image.new('RGBA', (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Caja más grande: 20% alto (la mitad) y 62% ancho (postal de record)
        box_h = int(self.HEIGHT * 0.20)
        box_w = int(self.WIDTH * 0.62)
        pad_x = 30
        pad_y = 10
        box = [int(self.WIDTH * 0.04), self.HEIGHT - box_h - int(self.WIDTH * 0.04),
               int(self.WIDTH * 0.04) + box_w, self.HEIGHT - int(self.WIDTH * 0.04)]
        self.rounded_rect(draw, box, 18, (0, 0, 0, 160))
        draw.rounded_rectangle(box, radius=18, outline=(245, 166, 35, 255), width=3)

        # Bandera de España, esquina superior derecha (5% x 5%)
        self.draw_spanish_flag(draw)

        font_call = self.get_font(36, bold=True)
        font_data = self.get_font(24)

        # Zona superior: datos (call, nombre, locator)
        top_area = box[1] + pad_y + 12
        line_h = 30
        y_call = top_area
        y_name = y_call + line_h
        y_loc = y_name + line_h

        # Línea 1: Callsign (dorado, llamativo)
        draw.text((box[0] + pad_x, y_call), call,
                  font=font_call, fill=(245, 166, 35, 255), anchor="lm")

        # Esquina inferior derecha: operador de la estación, en colores de bandera,
        # dentro de una minicaja con contraste (igual estilo que la caja de datos)
        station_text = STATION_TEXT
        font_station = self.get_font(36, bold=True)
        sbox = draw.textbbox((0, 0), station_text, font=font_station)
        sw, sh = sbox[2] - sbox[0], sbox[3] - sbox[1]
        spx, spy = 12, 8
        sxy = [self.WIDTH - 25 - sw - spx * 2,
               self.HEIGHT - 25 - sh - spy * 2,
               self.WIDTH - 25,
               self.HEIGHT - 25]
        self.rounded_rect(draw, sxy, 10, (0, 0, 0, 150))
        draw.rounded_rectangle(sxy, radius=10, outline=(255, 255, 255, 90), width=2)
        self.draw_flag_color_text(overlay, (sxy[0] + spx, sxy[1] + spy + sh / 2),
                                  station_text, font_station)

        # Línea 2: Nombre (con bandera del país delante)
        if name:
            fh = font_data.size
            x_name = box[0] + pad_x
            x_name = self.draw_station_flag(overlay, call, x_name, y_name, fh)
            draw.text((x_name, y_name), name,
                      font=font_data, fill=(255, 255, 255, 240), anchor="lm")

        # Línea 3: Grid locator
        if grid:
            draw.text((box[0] + pad_x, y_loc), f"Locator: {grid}",
                      font=font_data, fill=(255, 255, 255, 240), anchor="lm")

        # Casillas QSL1..QSL6: tilde en las 5 actividades logradas + bandera de España en la 6ª
        self.draw_activity_checkboxes(draw, box, checked={1, 2, 3, 4, 5},
                                      pad_x=pad_x, act_label="ACT", n=6, cw=28, ch=28,
                                      spacing=6, flag_box=6)

        result = Image.alpha_composite(img, overlay).convert('RGB')
        return result


def find_adi_files(folder):
    """Busca archivos ADI/ADIF en una carpeta (cualquier nombre, extensión case-insensitive).

    No duplica en sistemas de archivos case-insensitive (los globs *.adi + *.ADI
    matchearían el mismo archivo 2 veces).
    """
    adi = {f for f in folder.iterdir()
           if f.is_file() and f.suffix.lower() in ('.adi', '.adif')}
    return sorted(adi)


def folder_backgrounds(folder):
    """PNG/JPG de fondo propios de una carpeta (los del nivel raíz, no QSLS/)"""
    return sorted(
        list(folder.glob('*.png')) + list(folder.glob('*.jpg')) + list(folder.glob('*.jpeg'))
    )


def pick_background(backgrounds, index):
    """Alterna entre los fondos disponibles según el índice del contacto"""
    if not backgrounds:
        return None
    return backgrounds[index % len(backgrounds)]


# ============ Lógica de log ============

LOG_NAME = "qsl_log.json"


def sha256_file(path):
    """Hash SHA-256 de un archivo para detectar cambios"""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def load_log(folder):
    """Lee el log de una carpeta. Retorna dict {archivo: entry}"""
    log_path = folder / LOG_NAME
    if not log_path.exists():
        return {}
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_log(folder, log):
    """Escribe el log de una carpeta"""
    log_path = folder / LOG_NAME
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def png_valid(path):
    """Verifica que un PNG existe y se puede abrir correctamente"""
    if not path.exists():
        return False
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def prune_orphan_pngs(folder, log, label=""):
    """Elimina de QSLS/ los PNG que ya no referencia ningún ADI en el log.

    Evita acumular postales huérfanas cuando se borran contactos de un ADI
    o se elimina un ADI completo.
    """
    output_dir = folder / "QSLS"
    if not output_dir.exists():
        return 0
    referenced = set()
    for entry in log.values():
        for c in entry.get('contactos', []):
            arch = c.get('archivo')
            if arch:
                referenced.add(arch)
    removed = 0
    for f in output_dir.glob('*.png'):
        if f.name not in referenced:
            try:
                f.unlink()
                removed += 1
            except OSError:
                pass
    if removed:
        print(f"   🧹 {label}: {removed} postal/es huérfana/s eliminadas")
    return removed


def count_registered_pngs(folder):
    """Cuenta los PNG ya registrados en el log de una carpeta (secuencia de fondos local)"""
    total = 0
    log = load_log(folder)
    for entry in log.values():
        total += len(entry.get('contactos', []))
    return total


def sanitize_filename_component(text):
    """Convierte un callsign/procedencia en un componente de nombre seguro.

    Algunos logs traen prefijos/puertos (p.ej. 'EA5/XZZ', 'DL/N1ABC') que
    como hay '/' romperían la ruta del PNG.
    """
    s = re.sub(r'[^A-Za-z0-9_-]+', '_', text).strip('_')
    return s or 'unknown'


def unique_filenames(qsos, adi_stem):
    """
    Genera nombres de archivo únicos para un ADI.
    Formato: {callsign}_{adi_stem}.png (en minúsculas).
    Si un callsign se repite en el mismo ADI, se añade sufijo _2, _3...
    """
    stem = sanitize_filename_component(adi_stem)
    used = {}
    result = []
    for qso in qsos:
        call = sanitize_filename_component(qso.get('CALL') or 'unknown').lower()
        base = f"{call}_{stem}.png".lower()
        n = used.get(base, 0) + 1
        used[base] = n
        if n == 1:
            name = base
        else:
            name = f"{call}_{stem}_{n}.png"
        result.append(name)
    return result


def process_folder(folder, generator, backgrounds, seq):
    """Procesa los ADI de una carpeta usando el log."""
    output_dir = folder / "QSLS"
    output_dir.mkdir(exist_ok=True)

    # Actividad de la carpeta (qslN -> N) para tildar la casilla correcta
    try:
        activity = int(folder.name[3:])
    except ValueError:
        activity = None

    log = load_log(folder)
    adi_files = find_adi_files(folder)

    # Limpiar del log los ADI que ya no existen en disco
    existing = {f.name for f in adi_files}
    for name in list(log.keys()):
        if name not in existing:
            del log[name]
            print(f"   🗑️  {name}: ya no existe, eliminado del log")

    nuevos = 0
    regenerados = 0
    sin_cambios = 0

    def _render(qso, fn, prev_cont):
        """Renderiza una postal. Reutiliza el fondo previo si existe."""
        nonlocal seq
        bg_path = None
        if prev_cont is not None:
            pfondo = prev_cont.get('fondo')
            if isinstance(pfondo, str) and pfondo:
                cand = folder / pfondo
                if cand.exists():
                    bg_path = cand
                else:
                    for f in backgrounds:
                        if f.name == pfondo:
                            bg_path = f
                            break
        if bg_path is None:
            bg_path = pick_background(backgrounds, seq)

        seq += 1
        output_path = output_dir / fn
        postal = generator.compose(bg_path, qso, activity=activity)
        postal.save(output_path, 'PNG')

        return {
            'call': qso.get('CALL', 'unknown'),
            'archivo': fn,
            'fondo': bg_path.name,
            'generado_en': now_iso(),
        }

    for adi_file in adi_files:
        qsos = ADIFParser.parse(str(adi_file))
        file_hash = sha256_file(adi_file)
        entry = log.get(adi_file.name)
        prev_contacts = entry.get('contactos', []) if entry else []

        if entry is None or entry.get('sha256') != file_hash \
                or entry.get('generador') != GENERATOR_VERSION:
            # ===== Nuevo o modificado: reprocesar el ADI completo =====
            filenames = unique_filenames(qsos, adi_file.stem)
            contactos = []
            for idx, qso in enumerate(qsos):
                prev_cont = prev_contacts[idx] if idx < len(prev_contacts) else None
                contactos.append(_render(qso, filenames[idx], prev_cont))

            log[adi_file.name] = {
                'sha256': file_hash,
                'generador': GENERATOR_VERSION,
                'contactos': contactos,
                'procesado_en': now_iso(),
            }
            save_log(folder, log)
            nuevos += 1
            brief = ", ".join(c['archivo'] for c in contactos[:5])
            if len(contactos) > 5:
                brief += f", ... y {len(contactos) - 5} más"
            print(f"   ⚡ {adi_file.name}: {len(qsos)} contactos -> {brief}")
            continue

        # ===== Ya procesado: verificar que no falten PNGs =====
        faltantes = []
        for cont in entry.get('contactos', []):
            if not png_valid(output_dir / cont['archivo']):
                faltantes.append(cont)

        if not faltantes:
            sin_cambios += 1
            print(f"   ✓ {adi_file.name}: sin cambios ({len(qsos)} contactos ya generados)")
            continue

        # Regenerar solo los faltantes
        for cont in faltantes:
            idx = next((i for i, c in enumerate(prev_contacts)
                        if c.get('archivo') == cont.get('archivo')), None)
            qso = qsos[idx] if idx is not None else {}
            nuevo_cont = _render(qso, cont['archivo'], cont)
            # Actualizar la entrada en el log
            for i, c in enumerate(log[adi_file.name]['contactos']):
                if c.get('archivo') == cont['archivo']:
                    log[adi_file.name]['contactos'][i] = nuevo_cont
                    break
        regenerados += 1
        log[adi_file.name]['procesado_en'] = now_iso()
        save_log(folder, log)
        brief = ", ".join(c['archivo'] for c in faltantes[:5])
        if len(faltantes) > 5:
            brief += f", ... y {len(faltantes) - 5} más"
        print(f"   ♻️  {adi_file.name}: regenerados "
              f"{len(faltantes)} faltantes ({brief})")

    save_log(folder, log)
    prune_orphan_pngs(folder, log, label=folder.name)
    return nuevos, sin_cambios, regenerados, seq


def process_act6(base_dir, generator):
    """Actividad 6: genera una QSL de record en qsl6/QSLS/ para cada estación
    que contactó en TODAS las actividades (qsl1...qsl5).

    Muestra: callsign, nombre y grid locator.
    """
    qsl6 = base_dir / "qsl6"
    output_dir = qsl6 / "QSLS"
    output_dir.mkdir(exist_ok=True)

    # Las QSL6 son postales "de record": en cada ejecución se eliminan TODAS
    # para regenerarlas siempre con la información actual (nombres, grids,
    # banderas, versión del generador). No hay estado incremental.
    def _clean_output():
        n = 0
        for f in output_dir.glob("*.png"):
            try:
                f.unlink()
                n += 1
            except OSError:
                pass
        return n

    bgs = folder_backgrounds(qsl6)
    if not bgs:
        print(f"\n⚠️  QSL6: no tiene imagen de fondo propia (f6.png). No se generan records.")
        return 0, 0, 0

    print(f"\n📂 QSL6  (fondos: {', '.join(b.name for b in bgs)})")

    limpiadas = _clean_output()
    if limpiadas:
        print(f"   🗑️  QSL6/QSLS: {limpiadas} postal/es regenerada/s desde cero")

    # 1) Recolectar estaciones y su info en cada actividad
    act_names = [f"qsl{n}" for n in range(1, 6)]
    por_actividad = {}
    info_estacion = {}  # call -> {name, grid}
    for act in act_names:
        folder = base_dir / act
        calls = set()
        for adi in find_adi_files(folder):
            for qso in ADIFParser.parse(str(adi)):
                call = (qso.get('CALL') or '').strip()
                if not call:
                    continue
                call = call.upper()
                calls.add(call)
                if call not in info_estacion:
                    info_estacion[call] = {'name': '', 'grid': ''}
                if not info_estacion[call]['name']:
                    info_estacion[call]['name'] = (qso.get('NAME') or '').strip()
                if not info_estacion[call]['grid']:
                    info_estacion[call]['grid'] = (qso.get('GRIDSQUARE') or '').strip()
        por_actividad[act] = calls

    # 2) Intersección de las 5 actividades
    comunes = set.intersection(*por_actividad.values()) if por_actividad else set()
    if not comunes:
        print(f"   ℹ️  Ninguna estación contactó en las 5 actividades. Sin records que generar.")
        return 0, 0, 0

    print(f"   🏆 {len(comunes)} estación/es contactaron en las 5 actividades")

    # 3) Estado previo en log (solo informativo; la salida ya se limpió)
    log = load_log(qsl6)
    prev_entry = log.get("act6")
    prev_contacts = prev_entry.get('contactos', []) if prev_entry else []

    # Hash del conjunto actual (para el log)
    firma = "\n".join(sorted(
        f"{c}|{info_estacion[c]['name']}|{info_estacion[c]['grid']}" for c in comunes
    ))
    firma_hash = hashlib.sha256(firma.encode()).hexdigest()

    # Regeneración total en cada ejecución (las QSL6 siempre se regeneran:
    # la salida ya se limpió arriba, así que no hay nada que reutilizar).
    por_archivo = {c.get('archivo'): c for c in prev_contacts}
    contactos = []
    nuevos = 0
    regenerados = 0
    for call in sorted(comunes):
        fn = f"{sanitize_filename_component(call).lower()}_act6.png"
        info = info_estacion.get(call, {'name': '', 'grid': ''})
        prev = por_archivo.get(fn)
        # Regenerar (reusando el fondo previo si lo había)
        bg_path = None
        if prev and prev.get('fondo'):
            cand = qsl6 / prev['fondo']
            if cand.exists():
                bg_path = cand
            else:
                for f in bgs:
                    if f.name == prev['fondo']:
                        bg_path = f
                        break
        if bg_path is None:
            bg_path = bgs[0]
        postal = generator.compose_act6(bg_path, call, info['name'], info['grid'])
        postal.save(output_dir / fn, 'PNG')
        contactos.append({
            'call': call,
            'archivo': fn,
            'fondo': bg_path.name,
            'actividades': act_names,
            'generado_en': now_iso(),
        })
        if prev:
            regenerados += 1
        else:
            nuevos += 1

    log["act6"] = {
        'sha256': firma_hash,
        'generador': GENERATOR_VERSION,
        'contactos': contactos,
        'procesado_en': now_iso(),
    }
    save_log(qsl6, log)
    prune_orphan_pngs(qsl6, log, label="qsl6")

    nombres = ", ".join(f"{c['call']} → {c['archivo']}" for c in contactos[:5])
    if len(contactos) > 5:
        nombres += f", ... y {len(contactos) - 5} más"
    print(f"   ⚡ act6: {len(contactos)} record(s) -> {nombres}")
    return nuevos, regenerados, max(0, len(contactos) - nuevos - regenerados)


def main():
    print("=" * 60)
    print("  GENERADOR DE POSTALES QSL (incremental)")
    print("=" * 60)

    base_dir = Path(__file__).parent

    generator = QSLGenerator()
    total_nuevos = 0
    total_sin = 0
    total_regenerados = 0

    for i in range(1, 8):
        folder = base_dir / f"qsl{i}"
        if not folder.exists():
            continue

        # ===== Actividad 6: QSL de record, no usa ADIs propios =====
        if i == 6:
            nuevos, regenerados, sin_cambios = process_act6(base_dir, generator)
            total_nuevos += nuevos
            total_regenerados += regenerados
            total_sin += sin_cambios
            continue

        adi_files = find_adi_files(folder)
        if not adi_files:
            print(f"\n📂 {folder.name.upper()}  (sin archivos .adi, nada que generar)")
            continue

        # Fondos propios de la carpeta (los que estén en su raíz como .png/.jpg)
        folder_bgs = folder_backgrounds(folder)
        if not folder_bgs:
            print(f"\n⚠️  {folder.name.upper()}: no tiene imagen de fondo propia. "
                  f"Coloca una imagen .png en la carpeta.")
            continue

        print(f"\n📂 {folder.name.upper()}  (fondos: {', '.join(b.name for b in folder_bgs)})")
        # La secuencia de fondos arranca en el nº de PNG ya generados en esta carpeta
        seq = count_registered_pngs(folder)
        nuevos, sin_cambios, regenerados, seq = process_folder(
            folder, generator, folder_bgs, seq
        )
        total_nuevos += nuevos
        total_sin += sin_cambios
        total_regenerados += regenerados

    print("\n" + "=" * 60)
    print(f"  RESUMEN: {total_nuevos} procesados, {total_regenerados} regenerados, "
          f"{total_sin} sin cambios")
    print("  Log por carpeta: qslN/qsl_log.json")
    print("=" * 60)


if __name__ == "__main__":
    main()