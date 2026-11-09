#!/usr/bin/env python3.12
"""Generate GateShield store assets from SVG. Icon B = primary."""
import cairosvg, os

OUT = "/home/shaun/gateshield/assets"
os.makedirs(OUT, exist_ok=True)

# Icon B: shield + check, dark bg with green glow gradient (the pick)
ICON_B_BG = '''<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 512 512">
<defs>
 <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
   <stop offset="0" stop-color="#2a3a2a" stop-opacity="0.55"/>
   <stop offset="0.7" stop-color="#0d1117"/>
 </linearGradient>
</defs>
<rect width="512" height="512" rx="{r}" fill="#10151d"/>
<rect width="512" height="512" rx="{r}" fill="url(#bg)"/>
<rect x="2" y="2" width="508" height="508" rx="{r2}" fill="none" stroke="#39d353" stroke-opacity="0.35" stroke-width="4"/>
<g transform="translate(256,256) scale(0.8) translate(-256,-256)">
<path d="M256 96 400 148v156c0 130-91 208-144 234-53-26-144-104-144-234V148l144-52z" fill="none" stroke="#39d353" stroke-width="24" stroke-linejoin="round"/>
<path d="M186 262l52 52 96-104" fill="none" stroke="#39d353" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
</g>
</svg>'''

# Icon variants A, C, D
def icon_a(r, r2):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
<rect width="512" height="512" rx="{r}" fill="#1a2230"/>
<rect width="512" height="512" rx="{r}" fill="url(#ga)"/>
<defs><linearGradient id="ga" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#26304a"/><stop offset="1" stop-color="#10151d"/></linearGradient></defs>
<rect x="2" y="2" width="508" height="508" rx="{r2}" fill="none" stroke="#30363d" stroke-width="4"/>
<path d="M128 128h256M128 384h256" stroke="#39d353" stroke-width="18"/>
<path d="M168 128v180c0 66 56 118 88 140 32-22 88-74 88-140V128" fill="none" stroke="#39d353" stroke-width="18"/>
<path d="M256 360v52" stroke="#39d353" stroke-width="18"/></svg>'''

def icon_c(r, r2):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
<defs><linearGradient id="gc" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#39d353"/><stop offset="1" stop-color="#1a7f34"/></linearGradient></defs>
<rect width="512" height="512" rx="{r}" fill="url(#gc)"/>
<path d="M256 96 400 148v156c0 130-91 208-144 234-53-26-144-104-144-234V148l144-52z" fill="none" stroke="#0d1117" stroke-width="22" stroke-linejoin="round"/>
<path d="M186 262l52 52 96-104" fill="none" stroke="#0d1117" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/></svg>'''

def icon_d(r, r2):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
<defs><linearGradient id="gd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a3a2a" stop-opacity="0.55"/><stop offset="0.7" stop-color="#0d1117"/></linearGradient></defs>
<rect width="512" height="512" rx="{r}" fill="#10151d"/>
<rect width="512" height="512" rx="{r}" fill="url(#gd)"/>
<rect x="2" y="2" width="508" height="508" rx="{r2}" fill="none" stroke="#39d353" stroke-opacity="0.55" stroke-width="4"/>
<path d="M120 100h272M120 412h272" stroke="#39d353" stroke-width="26" stroke-linecap="round"/>
<path d="M156 100v180c0 70 62 124 100 148 38-24 100-78 100-148V100" fill="none" stroke="#39d353" stroke-width="26"/>
<path d="M256 380v40" stroke="#39d353" stroke-width="26" stroke-linecap="round"/></svg>'''

# Store banner 2 (the pick): gradient, badge, right icon
BANNER2 = '''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="500" viewBox="0 0 1024 500">
<defs>
 <linearGradient id="bg2" x1="0" y1="0" x2="1" y2="0.3">
  <stop offset="0" stop-color="#0d1117"/><stop offset="0.45" stop-color="#0d1117"/><stop offset="1" stop-color="#12211a"/>
 </linearGradient>
</defs>
<rect width="1024" height="500" fill="url(#bg2)"/>
<ellipse cx="900" cy="60" rx="260" ry="180" fill="#39d353" opacity="0.07"/>
<rect x="52" y="150" width="200" height="42" rx="21" fill="#39d353" fill-opacity="0.13" stroke="#39d353" stroke-opacity="0.35" stroke-width="1.5"/>
<text x="76" y="178" fill="#39d353" font-size="22" font-family="Menlo,monospace">/// scam protection</text>
<text x="52" y="262" fill="#e6edf3" font-size="58" font-weight="700" font-family="'Segoe UI',sans-serif">GateShield</text>
<text x="52" y="322" fill="#e6edf3" font-size="44" font-weight="700" font-family="'Segoe UI',sans-serif">Don't click. Scan first.</text>
<text x="52" y="376" fill="#8b949e" font-size="24" font-family="'Segoe UI',sans-serif">URL reputation · phishing heuristics · verdicts you can read</text>
<g transform="translate(800,140)">
 <rect width="180" height="180" rx="40" fill="#10151d"/>
 <rect width="180" height="180" rx="40" fill="url(#gb2)"/>
 <defs><linearGradient id="gb2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#39d353" stop-opacity="0.2"/><stop offset="0.7" stop-color="#0d1117"/></linearGradient></defs>
 <rect x="2" y="2" width="176" height="176" rx="38" fill="none" stroke="#39d353" stroke-opacity="0.5" stroke-width="2"/>
 <path d="M90 30 146 50v62c0 52-36 83-56 94-20-11-56-42-56-94V50l56-20z" fill="none" stroke="#39d353" stroke-width="9" stroke-linejoin="round"/>
 <path d="M66 102l21 21 39-42" fill="none" stroke="#39d353" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
</g>
</svg>'''

# Feature graphic: the approved bottom strip, scaled to 1024x500 with breathing room
FEATURE = '''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="500" viewBox="0 0 1024 500">
<rect width="1024" height="500" fill="#161b22"/>
<ellipse cx="880" cy="30" rx="300" ry="160" fill="#39d353" opacity="0.08"/>
<text x="70" y="235" fill="#e6edf3" font-size="72" font-weight="700" font-family="'Segoe UI',sans-serif">GateShield</text>
<text x="70" y="305" fill="#8b949e" font-size="30" font-family="'Segoe UI',sans-serif">The gate every link has to pass through.</text>
<text x="640" y="245" fill="#39d353" font-size="26" font-family="Menlo,monospace">/// safe</text>
<text x="640" y="285" fill="#ffb000" font-size="26" font-family="Menlo,monospace">/// caution</text>
<text x="640" y="325" fill="#ff5555" font-size="26" font-family="Menlo,monospace">/// danger</text>
</svg>'''

# Banner 1 (alternate, keep as option)
BANNER1 = '''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="500" viewBox="0 0 1024 500">
<defs><radialGradient id="rb" cx="0.8" cy="0" r="1"><stop offset="0" stop-color="#39d353" stop-opacity="0.15"/><stop offset="1" stop-color="#39d353" stop-opacity="0"/></radialGradient></defs>
<rect width="1024" height="500" fill="#161b22"/>
<rect width="1024" height="500" fill="url(#rb)"/>
<g transform="translate(90,160)">
 <rect width="180" height="180" rx="40" fill="#10151d"/>
 <rect x="2" y="2" width="176" height="176" rx="38" fill="none" stroke="#39d353" stroke-opacity="0.5" stroke-width="2"/>
 <path d="M90 30 146 50v62c0 52-36 83-56 94-20-11-56-42-56-94V50l56-20z" fill="none" stroke="#39d353" stroke-width="9" stroke-linejoin="round"/>
 <path d="M66 102l21 21 39-42" fill="none" stroke="#39d353" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
</g>
<text x="330" y="235" fill="#e6edf3" font-size="60" font-weight="700" font-family="'Segoe UI',sans-serif">GateShield</text>
<text x="330" y="290" fill="#8b949e" font-size="26" font-family="'Segoe UI',sans-serif">Scan any link. Pass it through the gate.</text>
</svg>'''

# favicon/mark (transparent, shield only)
MARK = '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
<path d="M256 64 416 120v170c0 142-100 226-160 254-60-28-160-112-160-254V120l160-56z" fill="none" stroke="#39d353" stroke-width="24" stroke-linejoin="round"/>
<path d="M178 262l56 56 100-108" fill="none" stroke="#39d353" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/></svg>'''

def render(svg, name, w, h):
    cairosvg.svg2png(bytestring=svg.encode(), write_to=f"{OUT}/{name}", output_width=w, output_height=h)
    print("wrote", name)

# --- icons: all 4 at all sizes (B first = primary) ---
variants = {"A": icon_a, "C": icon_c, "D": icon_d}
for size in (512, 432, 192, 96, 48):
    r = int(size * 0.22); r2 = r - 3
    render(ICON_B_BG.format(s=size, r=r, r2=r2), f"iconB-{size}.png", size, size)
    render(icon_a(r, r2), f"iconA-{size}.png", size, size)
    render(icon_c(r, r2), f"iconC-{size}.png", size, size)
    render(icon_d(r, r2), f"iconD-{size}.png", size, size)

# Play Store icon must be full-square 512 (no rounded baked) — also make flat 512 of B
FLAT = ICON_B_BG.format(s=512, r=0, r2=2)
render(FLAT, "iconB-playstore-512.png", 512, 512)
render(MARK, "mark-512.png", 512, 512)
render(MARK, "mark-192.png", 192, 192)
render(MARK, "favicon-48.png", 48, 48)

# --- banners ---
render(BANNER2, "banner-pick-1024x500.png", 1024, 500)
render(BANNER1, "banner-alt-1024x500.png", 1024, 500)
render(FEATURE, "feature-graphic-1024x500.png", 1024, 500)
print("DONE")
