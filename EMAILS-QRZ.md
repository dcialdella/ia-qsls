# Emails de QRZ.COM para la lista de indicativos

Fecha: 2026-11-18 · Fuente: fichas de QRZ.COM consultadas con sesión iniciada.

> **Privacidad:** la cookie de sesión se guardó temporalmente fuera del repo con
> `chmod 600` y se **eliminó** al terminar. Ni la cookie ni ninguna credencial
> están versionadas. Los emails son datos publicados por sus titulares en su
> ficha pública de QRZ.

## Procedimiento reutilizable

1. El usuario aporta la cookie de sesión de QRZ (`qrz_cookie.json`) en una ruta
   temporal fuera del repo. Se extraen las *request headers* y se eliminan `Host`
   y `Accept-Encoding` (para evitar respuestas comprimidas sin decodificar).
2. Se pide `https://www.qrz.com/db/<INDICATIVO>` con esas headers y un
   `User-Agent` de navegador real (Firefox 160.0), `Referer: https://www.qrz.com/`.
   Importante: **no forzar `Host`** al consultar `www.qrz.com`.
3. QRZ ofusca el email en `var qmail = '<cadena>'` mediante JavaScript. El
   descodificador es la inversa de la función `showqem()` de la propia página:

   ```python
   def decode_qmail(cem):
       cl, i = '', len(cem) - 1
       while i > 0:
           if cem[i] != '!':
               cl += cem[i]
           else:
               break
           i -= 1
       i -= 1
       dem = ''
       for _ in range(int(cl)):       # cl es el número de iteraciones, en orden inverso
           dem += cem[i]
           i -= 2                     # se saltan 2 caracteres en cada paso
       return dem
   ```

   Ejemplo: `f81b1e6c5cam1o0cb.4lai0a2m1t6oche@2p5h8af14ace!81` →
   `ea1ahp@hotmail.com`.
4. QRZ limita las consultas: tras ~8 peticiones seguidas devuelve **HTTP 429**.
   Hay que esperar el `Retry-After` (~65 s) y reintentar; con pausa de ~7 s entre
   indicativos se completó la lista sin más bloqueos.
5. Los resultados se vuelcan a un JSON temporal (`qrz_emails.json`) y, al terminar,
   se borran tanto ese archivo como la cookie. **No dejar credenciales en disco.**

## Resultados

**35 de 38** indicativos tienen email visible en QRZ.

| Indicativo | Email | Estado |
|---|---|---|
| T1BSC | — | sin ficha en QRZ |
| EA1AHP | ea1ahp@hotmail.com | ok |
| EA1AMA | candidofra@gmail.com | ok |
| EA1DFP | ea1dfp@movistar.es | ok |
| EA1FB | joseramon.ea1fb@gmail.com | ok |
| EA1GM | radioelectrica@gmail.com | ok |
| EA1MJ | EA1MJ@hotmail.com | ok |
| EA1RCU | ea1rcu.u30@gmail.com | ok |
| EA1SAL | eb1gks@gmail.com | ok |
| EA3ABP | — | ficha existe, sin email publicado |
| EA3CYM | ea3cym@gmail.com | ok |
| EA3GUN | eugeniradio@gmail.com | ok |
| EA3HIC | — | sin ficha en QRZ |
| EA4AAI | gerardocampo@telefonica.net | ok |
| EA4DIZ | luis.alb@telefonica.net | ok |
| EA4FTV | ea4ftv@gmail.com | ok |
| EA4GJP | ea4gjp@hotmail.com | ok |
| EA4IFN | EA4IFN@outlook.es | ok |
| EA5BX | mayanor@telefonica.net | ok |
| EA5EM | ea5em@hotmail.com | ok |
| EA5GUQ | pedroea50guq@gmail.com | ok |
| EA5HKZ | ea5hkz.gps@outlook.es | ok |
| EA5IIG | ea5iig@hotmail.com | ok |
| EA7DQH | ajmm1951@outlook.es | ok |
| EA7E | ea7e.pedro@gmail.com | ok |
| EA7GRB | ea7grb@hotmail.com | ok |
| EA7HOH | ea7hoh@gmail.com | ok |
| EA7HZ | ea7hz@hotmail.com | ok |
| EA7JM | ea7jm.suso@gmail.com | ok |
| EA7KOY | ea7koy@gmail.com | ok |
| EA7LEI | emiliogarcialopez.far@gmail.com | ok |
| EA7OY | ecoalfa7oy@gmail.com | ok |
| EA7UW | rricmillan@gmail.com | ok |
| EA9PD | ea9pd@hotmail.com | ok |
| EB4FZI | eb4fzi@gmail.com | ok |
| EB7FSB | eb7fsb@gmail.com | ok |
| EC7DZZ | ir271javier@hotmail.com | ok |
| IK1GPG | ik1gpg@alice.it | ok |

### Lista plana (35 emails, separados por coma)

```text
ea1ahp@hotmail.com, candidofra@gmail.com, ea1dfp@movistar.es, joseramon.ea1fb@gmail.com, radioelectrica@gmail.com, EA1MJ@hotmail.com, ea1rcu.u30@gmail.com, eb1gks@gmail.com, ea3cym@gmail.com, eugeniradio@gmail.com, gerardocampo@telefonica.net, luis.alb@telefonica.net, ea4ftv@gmail.com, ea4gjp@hotmail.com, EA4IFN@outlook.es, mayanor@telefonica.net, ea5em@hotmail.com, pedroea50guq@gmail.com, ea5hkz.gps@outlook.es, ea5iig@hotmail.com, ajmm1951@outlook.es, ea7e.pedro@gmail.com, ea7grb@hotmail.com, ea7hoh@gmail.com, ea7hz@hotmail.com, ea7jm.suso@gmail.com, ea7koy@gmail.com, emiliogarcialopez.far@gmail.com, ecoalfa7oy@gmail.com, rricmillan@gmail.com, ea9pd@hotmail.com, eb4fzi@gmail.com, eb7fsb@gmail.com, ir271javier@hotmail.com, ik1gpg@alice.it
```

## Casos sin email y búsqueda en internet

- **`T1BSC`**: QRZ devuelve «no results». Si es un typo de **`CT1BSC`**, esa ficha
  sí existe y su email (descodificado igual) es `j.p.alvaro@sapo.pt`. Confirmar
  con el usuario antes de usarlo.
- **`EA3ABP`**: la ficha de QRZ existe (JERONIMO "JERO" M.N., Tarragona), pero el
  operador **no ha publicado email**. Búsquedas en fuentes públicas:
  - QRZCQ: ficha pasiva, «Javier, Spain», locator IN80DJ, sin email.
  - HamQTH: 404 (sin ficha).
  - DXMaps: EA3ABP en JN01SH (2024-11-28).
  - Google (nombre, `@`, gmail/hotmail/telefonica/yahoo): sin dirección pública.
    El único «Jeronimo Martín» de Tarragona que aparece es un abogado en
    LinkedIn, sin relación confirmada con el indicativo; no usar.
- **`EA3HIC`**: QRZ devuelve «no results». Fuentes públicas:
  - QRZCQ: ficha pasiva, «ALFONSO, Spain», locator genérico IN80AA, sin email.
  - HamQTH: 404 (sin ficha).
  - DMUE (radiogalena.es): 1.040 QSO en SSB, sin datos de contacto.
  - Google (nombre, `@`, proveedores de correo, QSL directa): sin dirección pública.
  - No confundir con `EA3HIF` (Carlos, Badalona): es otro indicativo.

**Conclusión:** no hay emails públicos fiables para esos tres indicativos. Vía
recomendada para ellos: QSL por Bureau/directa o eQSL/LoTW.
