# Renders the monitor bezel as a 9-slice frame image for CSS border-image.
#
# Geometry: four flat faces sloping from the front of the housing down to the tube. At a corner two faces simply meet
# along the diagonal; every pixel belongs to the face whose outer edge is nearest, so each corner triangle is a plain
# continuation of its own face (same tone, same falloff, same grain direction). No extra faces.
#
# Per face: a flat tone set by how it faces the light (top in shadow, bottom lit, left shaded, right slightly lit),
# a small radius where the front face turns into the slope, a slight darkening toward the tube, and satin grain
# compressed along the slope because the face is seen at an angle. Creases between faces are softened over ~1px.
#
# usage: make-bezel.py <out.png>
import sys
from PIL import Image, ImageFilter

SCALE = 2                 # image pixels per CSS pixel
B = 18 * SCALE            # bezel width (border-image-slice)
L = 256 * SCALE           # length of the repeating edge tile
W = B + L + B
SS = 3                    # supersampling per axis

HOUSING = 35.0                                            # front-face tone (#232321)
TONE = {"top": 25.0, "bottom": 67.0, "left": 30.5, "right": 53.0}
EDGE_RADIUS = 3 * SCALE   # width of the turn-over at the outer edge
CREASE = 1.0 * SCALE      # softening width where two faces meet
AO = 0.24                 # darkening at the tube end of each face
SQUASH = 3.5              # grain compression along the slope

# seamless satin noise, values roughly in [-1, 1]
N = 512
noise = Image.effect_noise((N, N), 40)
big = Image.new("L", (N * 3, N * 3))
for i in range(3):
    for j in range(3):
        big.paste(noise, (i * N, j * N))
soft = big.filter(ImageFilter.GaussianBlur(0.55)).crop((N, N, N * 2, N * 2))
npx = soft.load()


def grain(along, depth, salt):
    return (npx[int(along + salt) % N, int(depth * SQUASH + salt * 3) % N] - 128) / 22.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def face_tone(name, depth):
    turn = smooth(depth / EDGE_RADIUS)                    # 0 at the outer edge, 1 once on the face
    tone = HOUSING + (TONE[name] - HOUSING) * turn
    return tone * (1 - AO * (depth / B) ** 1.5)


def sample(x, y):
    """Tone at a sub-pixel position, or None outside the ring."""
    d = {"top": y, "bottom": W - y, "left": x, "right": W - x}
    order = sorted(d, key=d.get)
    a, b = order[0], order[1]
    if d[a] >= B:
        return None
    along_a = x if a in ("top", "bottom") else y
    va = face_tone(a, d[a])
    va += grain(along_a, d[a], {"top": 0, "bottom": 97, "left": 211, "right": 331}[a]) * (0.05 * va + 1.0)
    gap = d[b] - d[a]
    if gap < CREASE:                                      # near a crease: ease into the neighbouring face
        along_b = x if b in ("top", "bottom") else y
        vb = face_tone(b, d[b])
        vb += grain(along_b, d[b], {"top": 0, "bottom": 97, "left": 211, "right": 331}[b]) * (0.05 * vb + 1.0)
        w = 0.5 * smooth(1 - gap / CREASE)                # 0.5 on the diagonal, 0 at CREASE away
        va = va * (1 - w) + vb * w
    return va


img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
out = img.load()
for py in range(W):
    for px in range(W):
        if B <= px < W - B and B <= py < W - B:
            continue
        total, hits = 0.0, 0
        for sy in range(SS):
            for sx in range(SS):
                v = sample(px + (sx + 0.5) / SS, py + (sy + 0.5) / SS)
                if v is not None:
                    total += v
                    hits += 1
        if hits:
            g = max(0, min(255, round(total / hits)))
            # warm grey, matching the housing colour #232321
            out[px, py] = (g, g, g, round(255 * hits / (SS * SS)))
img.save(sys.argv[1], optimize=True)
print("wrote", sys.argv[1], img.size, "slice", B)
