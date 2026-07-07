#!/usr/bin/env python3
# Собирает инлайн-разметку декора и вставляет её в index.html между
# маркерами <!--DECO-LEFT--> и <!--DECO-RIGHT-->.
#
# Каждый .deco несёт ОБА набора координат в инлайн-переменных:
#   ДЕСКТОП (--dx/--dy/--dw/--dh, --rot):
#     координаты внутри desktop-кластера в px из Figma-1920;
#     позиции считает CSS через --u (десктопная единица).
#   МОБИЛКА (--dmx/--dmy/--dmw/--dmh):
#     координаты и размер В PX внутри мобильного фрейма 402x874 из Figma;
#     CSS-медиазапрос применяет их через --um = calc(100vw/402).
#     Верхняя полоса на мобилке = левый кластер, нижняя = правый.
# --rot общий для обоих режимов.
#
# Элемент помечается extra-классом (см. поля с 4-м/8-м элементом):
#   deco--mouse-dot-l / deco--mouse-dot-r — точки-компаньоны мыши;
#   deco--m-hide — скрыть на мобилке (лишние круги/точки).
import re, pathlib, math


def rendered_w(dw, dh, rot):
    """Ширина axis-aligned bounding box повёрнутого прямоугольника."""
    r = math.radians(abs(rot))
    return dw * math.cos(r) + dh * math.sin(r)

HERE = pathlib.Path(__file__).parent
INDEX = HERE.parent.parent / "index.html"

# =========================================================================
# КРУГИ (заливка, без SVG)
# формат: (desk_x, desk_y, desk_d, extra_class,   mob_x, mob_y, mob_d)
# desk_x/desk_y — левый-верхний угол в кластере desktop;
# mob_x/mob_y   — левый-верхний угол в мобильном фрейме 402 (0 если скрыт).
# =========================================================================
# мобильные (mx,my,mw) — ТОЧНЫЕ абсолютные координаты в Figma-фрейме 402×874
#   На мобилке остаётся только 4 иконки (iphone/coffee/html/folder),
#   4 звезды и 2 больших блоба (по одному в каждом углу). Всё лишнее hidden.
left_circles = [
    (128.0, 192.0, 270, "",                                17.0,  122.86, 71.84),  # большой блоб слева
    (0.0,   28.0,  150, "deco--m-hide",                     0,    0,     0),
    (118.0, 498.0, 120, "deco--m-hide",                     0,    0,     0),
    (415.0, 46.0,  25,  "deco--m-hide",                     0,    0,     0),
    (45.0,  309.0, 25,  "deco--m-hide",                     0,    0,     0),
    (271.1, 566.5, 25,  "deco--mouse-dot-l deco--m-hide",   0,    0,     0),
    (407.1, 490.5, 25,  "deco--mouse-dot-r deco--m-hide",   0,    0,     0),
]
right_circles = [
    (160.0, 254.0, 250, "",                                310.0, 139.58, 70.01),  # блоб (за предметами)
    (171.0, 0.0,   150, "deco--m-hide",                    0,    0,     0),
    # два маленьких круга-блоба слева от макбука → двигаются с ним (десктоп)
    (16.0,  121.0, 25,  "deco--r-blob-mac deco--m-hide",   0,    0,     0),
    (44.0,  315.0, 25,  "deco--r-blob-mac deco--m-hide",   0,    0,     0),
]

# =========================================================================
# ЗНАЧКИ
# формат: (файл, desk_cx, desk_cy, rot,  mob_x, mob_y, mob_w, mob_h)
# desk_cx/desk_cy — центр в кластере desktop; mob_x/mob_y — левый-верхний
# угол в мобильном фрейме 402 (из Figma); mob_w/mob_h — размер там же.
# =========================================================================
#   Мобильные (mx,my,mw,mh) — ТОЧНЫЕ абсолютные координаты в Figma-фрейме
#   402×874 (node «hero телефон»). Ничего не раздвигаем: пары/звёзды/линии
#   стоят ровно как в макете, кончики линий у остриёв.
left_icons = [
    #  файл       desk_cx desk_cy rot     mob_x   mob_y   mob_w   mob_h
    ("folder",   146.1, 205.3,   0.0,   335.59, 183.30,  54.82,  50.12),  # моб. — правый низ
    ("cursor",   373.7, 131.7, -22.6,    79.08, 151.21,  40.36,  43.91),  # скрыт на моб (m-hide в CSS)
    ("iphone",   428.4, 309.6,   5.3,    38.72,  88.00,  35.65,  62.37),  # моб. — левый верх
    ("html",     138.3, 486.3,   5.3,    33.00, 190.71,  59.19,  65.56),  # моб. — левый низ
    ("mouse",    344.5, 536.4, -12.7,    70.00,  42.06,  53.56,  68.31),  # скрыт на моб
    ("star3",    320.0, 340.0,  14.4,    18.00, 131.50,  13.45,  13.45),  # звезда СЛЕВА от айфона (с отступом)
    ("star2",    527.0, 246.0, -22.2,    79.17,  93.00,  14.41,  14.41),  # звезда СПРАВА от айфона (с отступом)
    ("line5",    274.2,  57.1, -148.0,   70.00, 151.68,  63.37,  60.01),  # скрыт на моб
]
right_icons = [
    #  файл       desk_cx desk_cy rot     mob_x   mob_y   mob_w   mob_h
    ("macbook",  160.4, 172.6,   0.0,    51.06, 675.00, 140.88, 125.25),  # скрыт на моб
    ("css",      428.5, 259.5,  12.0,   205.73, 720.00,  91.56,  99.09),  # скрыт на моб
    ("stylus",   369.4, 578.9, -10.6,    22.00, 795.17,  53.41,  59.73),  # скрыт на моб
    ("line4",    402.4, 649.5,   0.0,    32.79, 847.06,  64.57,   7.79),  # скрыт на моб
    ("coffee",   164.0, 484.5,   0.0,   317.46,  82.00,  62.43,  80.79),  # моб. — правый верх
    ("star5",    269.0, 408.0,  20.5,   379.76,  92.52,  13.81,  13.81),  # звезда справа-сверху, посередине
    ("star6",    418.0,  93.0,  -9.1,    56.00, 685.58,  18.69,  18.69),  # скрыт на моб (за краем — ок)
    ("star4",     70.0, 578.0,  25.2,   319.44, 157.59,  14.27,  14.27),  # звезда слева-снизу, посередине
]


def read_svg(name):
    return (HERE / f"{name}.svg").read_text(encoding="utf-8").strip()


def viewbox(svg):
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    return float(m.group(1)), float(m.group(2))


def anim_class(name):
    if name in ("line4", "line5"):
        return "deco--draw"
    if name.startswith("star"):
        return "deco--twinkle"
    if name == "cursor":
        return "deco--tip deco--cursor"
    if name == "stylus":
        return "deco--tip deco--stylus"
    return "deco--float"


# TIP-companions: {name: (leader_cx, leader_cy)} — курсор/стилус и их линии.
# Позиция = анкор·u + offset·u_size → двигаются ВМЕСТЕ с полосой (лидером),
# при этом кончик линии остаётся на острие (anchor общий).
TIP_COMPANIONS = {
    "cursor": (323.95,  94.4),
    "line5":  (323.95,  94.4),
    "stylus": (385.9,  614.2),
    "line4":  (385.9,  614.2),
    # звёзды у кофе — вплотную к чашке, позиции фиксированные к её центру
    "star5":  (164.0, 484.5),
    "star4":  (164.0, 484.5),
}
# STAR-companions: {name: (anchor_cx, anchor_cy, anchor_w, side_x)}
# Звезда стоит с ПОСТОЯННЫМ отступом от края объекта (CSS считает по
# --anchor-w и --side-x + фикс. gap), поэтому зазор одинаков на всех ширинах.
# {name: (anchor_cx, anchor_cy, anchor_rendered_w, side_x)}
# anchor_rendered_w — bbox-ширина лидера с учётом его поворота.
# Зазор от края объекта до края звезды считается по РЕНДЕР-ширинам
# обоих (--anchor-rw и --star-rw) + фикс. gap → ровно 5px везде.
STAR_COMPANIONS = {
    "star2": (428.4, 309.6, rendered_w(81.333, 159.596, 5.3),  1),  # справа от iphone
    "star3": (428.4, 309.6, rendered_w(81.333, 159.596, 5.3), -1),  # слева от iphone
    "star6": (160.4, 172.6, rendered_w(320.776, 285.188, 0),   1),  # справа от макбука
}
STAR_VB = 32.7173  # viewBox звезды (квадрат)


def style_vars(cx, cy, ox, oy, dw, dh, rot, mx, my, mw, mh, extra=""):
    return (f"--cx:{cx:.2f};--cy:{cy:.2f};--ox:{ox:.2f};--oy:{oy:.2f};"
            f"--dw:{dw:.3f};--dh:{dh:.3f};--rot:{rot}deg{extra};"
            f"--dmx:{mx:.2f};--dmy:{my:.2f};--dmw:{mw:.3f};--dmh:{mh:.3f}")


def circle_html(x, y, d, extra, mx, my, mw):
    st = style_vars(x + d/2, y + d/2, 0, 0, d, d, 0, mx, my, mw, mw)
    cls = "deco deco-circle deco--blob" + (f" {extra}" if extra else "")
    return f'      <span class="{cls}" style="{st}"></span>'


def icon_html(name, cx, cy, rot, mx, my, mw, mh):
    svg = read_svg(name)
    a, b = viewbox(svg)
    extra = ""
    if name in TIP_COMPANIONS:
        acx, acy = TIP_COMPANIONS[name]
        ox, oy = cx - acx, cy - acy
    elif name in STAR_COMPANIONS:
        acx, acy, arw, sx = STAR_COMPANIONS[name]
        ox, oy = 0, cy - acy          # X — по gap-формуле, Y — вертик. смещение
        srw = rendered_w(a, b, rot)   # рендер-ширина самой звезды
        extra = f";--anchor-rw:{arw:.3f};--star-rw:{srw:.3f};--side-x:{sx}"
    else:
        acx, acy = cx, cy
        ox, oy = 0, 0
    st = style_vars(acx, acy, ox, oy, a, b, rot, mx, my, mw, mh, extra)
    return (f'      <span class="deco deco-{name} {anim_class(name)}" '
            f'style="{st}">{svg}</span>')


def build(circles, icons):
    out = ["", "      <!-- фоновые круги -->"]
    out += [circle_html(*c) for c in circles]
    out += ["      <!-- значки -->"]
    out += [icon_html(*i) for i in icons]
    out += ["    "]
    return "\n".join(out)


html = INDEX.read_text(encoding="utf-8")
html = re.sub(r"<!--DECO-LEFT-->.*?(?=\n\s*</div>)",
              "<!--DECO-LEFT-->" + build(left_circles, left_icons),
              html, count=1, flags=re.S)
html = re.sub(r"<!--DECO-RIGHT-->.*?(?=\n\s*</div>)",
              "<!--DECO-RIGHT-->" + build(right_circles, right_icons),
              html, count=1, flags=re.S)
INDEX.write_text(html, encoding="utf-8")
print("index.html обновлён")
