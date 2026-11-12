#!/usr/bin/env python3
"""Extract recipes from the two cookbook PDFs into recipes.json + img/*.webp.

Usage: build.py <meal-prep-cookbook.pdf> <digital-cookbook.pdf> <out-dir> [--no-images]

The PDFs are purchased books and are NOT part of this repo; neither is the
output. Keep both out of version control.
"""
import io
import json
import re
import sys
from pathlib import Path

import pymupdf
from PIL import Image

from canon import canon_for, CANON  # noqa: E402


def lines_of(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            spans = [s for s in l["spans"] if s["text"].strip()]
            if not spans:
                continue
            text = "".join(s["text"] for s in l["spans"]).replace("\t", " ")
            text = re.sub(r"\s+", " ", text).strip()
            s = spans[0]
            x0, y0, x1, y1 = l["bbox"]
            out.append(dict(x=x0, y=y0, x1=x1, y1=y1, t=text, size=s["size"],
                            font=s["font"], color=s["color"]))
    return out


def clean(t):
    t = t.replace("»»", "").replace("»", "").strip()
    t = t.replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", t).strip()


def join(parts):
    s = ""
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if s.endswith("-") and not s.endswith(" -") and p[:1].islower():
            s = s + p
        else:
            s = (s + " " + p) if s else p
    return clean(s)


def spaced(t):
    toks = t.split()
    return len(toks) >= 3 and sum(len(x) <= 2 for x in toks) / len(toks) > 0.6


def links_of(page):
    v = {}
    for l in page.get_links():
        u = l.get("uri") or ""
        if "youtu" in u:
            v["yt"] = u
        elif "tiktok" in u:
            v["tt"] = u
        elif "instagram" in u:
            v["ig"] = u
    return v


def save_image(doc, page, dest, crop_top=0.0):
    best = None
    for im in page.get_images(full=True):
        w, h = im[2], im[3]
        if best is None or w * h > best[1]:
            best = (im[0], w * h)
    if not best:
        return False
    raw = doc.extract_image(best[0])["image"]
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    if crop_top:
        img = img.crop((0, int(img.height * crop_top), img.width, img.height))
    w = 640
    img = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
    img.save(dest, "WEBP", quality=62, method=6)
    return True


# ---------- ingredient blocks ----------

def parse_ingredients(lines, dash=True):
    """lines: already in reading order. Returns [{group, items[]}]."""
    groups = []
    cur = None
    for l in lines:
        t = l["t"]
        if "Continue" in t and len(t) < 14:
            continue
        is_item = l.get("bullet") or (dash and re.match(r"^[–\-•]\s*", t))
        if is_item:
            t = re.sub(r"^[–\-•]\s*", "", t)
            if cur is None:
                cur = dict(group="", items=[])
                groups.append(cur)
            cur["items"].append(clean(t))
        elif l.get("header"):
            if cur is not None and not cur["items"] and cur["group"]:
                cur["group"] = join([cur["group"], t]).rstrip(":")
            else:
                cur = dict(group=clean(t).rstrip(":"), items=[])
                groups.append(cur)
        else:
            if cur and cur["items"]:
                cur["items"][-1] = join([cur["items"][-1], t])
            elif cur is not None and not cur["items"]:
                cur["group"] = join([cur["group"], t])
            else:
                cur = dict(group="", items=[clean(t)])
                groups.append(cur)
    return [g for g in groups if g["items"] or g["group"]]


# ---------- book 1 ----------

def book1(doc, out, images):
    recs = []
    n = len(doc)
    for i in range(n - 1):
        cover = lines_of(doc[i])
        m = None
        for l in cover:
            m = re.match(r"Recipe # ?(\d+)", l["t"])
            if m:
                break
        if not m:
            continue
        batch = (i + 1) >= 237
        num = int(m.group(1))
        title = join([l["t"] for l in sorted(cover, key=lambda l: l["y"])
                      if "Bingo" in l["font"] and l["size"] > 20])
        allt = " ".join(l["t"] for l in cover)
        mk = re.search(r"MAKES (\d+)", allt)
        nums = sorted([l for l in cover if re.fullmatch(r"\d+ ?g?", l["t"]) and l["size"] >= 13],
                      key=lambda l: (round(l["y"] / 8), l["x"]))
        vals = [int(re.sub(r"\D", "", l["t"])) for l in nums]
        macros = vals[:4]
        with_sauce = vals[4:8] if len(vals) >= 8 else None
        desc = join([l["t"] for l in sorted(cover, key=lambda l: l["y"])
                     if 11.5 <= l["size"] <= 13 and "DMSans" in l["font"]
                     and not re.fullmatch(r"[A-Z ]+", l["t"]) and l["y"] > 250])
        data = lines_of(doc[i + 1])
        heads = sorted([l for l in data if l["size"] >= 15 and "SemiBold" in l["font"]],
                       key=lambda l: l["y"])
        sect = {}
        for k, h in enumerate(heads):
            y0 = h["y1"] - 2
            y1 = heads[k + 1]["y"] - 2 if k + 1 < len(heads) else 800
            body = [l for l in data if y0 <= l["y"] < y1 and l is not h and l["size"] < 15]
            key = h["t"].split("(")[0].strip().upper()
            sect[key] = (h, body)
        servings = mk.group(1) if mk else None
        ing = []
        steps = []
        notes = []
        serve = []
        sauces = []
        for key, (h, body) in sect.items():
            if key.startswith("INGREDIENTS"):
                starts = [l["x"] for l in body if re.match(r"^[–\-]\s", l["t"])]
            elif key.startswith("INSTRUCTIONS"):
                starts = [l["x"] + 7 for l in body if re.match(r"^z?STEP\d", l["t"].replace(" ", ""))]
            else:
                starts = []
            anchors = []
            for a in sorted(starts):
                if not anchors or a - anchors[-1] > 60:
                    anchors.append(a)
            anchors = anchors or [44]
            cols = [[] for _ in anchors]
            for l in body:
                k = max([j for j, a in enumerate(anchors) if l["x"] >= a - 12] or [0])
                l["ax"] = anchors[k]
                cols[k].append(l)
            cols = [sorted(c, key=lambda l: l["y"]) for c in cols]
            if key.startswith("INGREDIENTS"):
                sm = re.search(r"\((\d+)", h["t"])
                if sm and not servings:
                    servings = sm.group(1)
                seq = []
                for c in cols:
                    if not c:
                        continue
                    for l in c:
                        base = l["ax"] - 5
                        isdash = re.match(r"^[–\-]\s", l["t"])
                        l["header"] = (not isdash) and (l["x"] - base) < 5 and (
                            l["size"] > 10.2 or bool(re.search(r"\)$|Mix|Sauce|Marinade", l["t"])))
                        if not isdash and not l["header"] and (l["x"] - base) < 5 and l["size"] <= 10.2 \
                                and re.match(r"^(You will|Use |Note)", l["t"]):
                            l["t"] = "– " + l["t"]
                        seq.append(l)
                ing = parse_ingredients(seq)
            elif key.startswith("INSTRUCTIONS"):
                cur = None
                for c in cols:
                    for l in c:
                        t = l["t"]
                        ns = t.replace(" ", "")
                        sm = re.match(r"^z?STEP(\d+)", ns)
                        if sm:
                            cur = []
                            steps.append(cur)
                            continue
                        if "Continue" in t and len(t) < 14:
                            continue
                        if spaced(t) or "Wingdings" in l["font"]:
                            continue
                        if cur is None:
                            cur = []
                            steps.append(cur)
                        cur.append(t)
                steps = [join(s) for s in steps if s]
            else:
                marks = [l for l in body if l["t"] in ("z",) or "Wingdings" in l["font"]]
                txt = sorted([l for l in body if l not in marks], key=lambda l: l["y"])
                items = []
                for l in txt:
                    t = l["t"]
                    isdash = re.match(r"^[–\-]\s", t)
                    bul = any(abs(mk_["y"] - l["y"]) < 7 for mk_ in marks)
                    if isdash or bul:
                        items.append([re.sub(r"^[–\-]\s*", "", t)])
                    elif items and not key.startswith(("BEST", "SAUCE")):
                        items[-1].append(t)
                    elif items and l["x"] > 50:
                        items[-1].append(t)
                items = [join(x) for x in items]
                if key.startswith("IMPORTANT"):
                    notes = items
                elif key.startswith("BEST"):
                    serve = items
                elif key.startswith("SAUCE"):
                    sauces = items
        rid = f"a{i + 1:03d}"
        r = dict(id=rid, book=1, page=i + 1, num=num, title=title,
                 cat="batch" if batch else "prep",
                 cal=macros[0] if macros else None, pro=macros[1] if len(macros) > 1 else None,
                 carb=macros[2] if len(macros) > 2 else None, fat=macros[3] if len(macros) > 3 else None,
                 serves=servings or "", desc=desc, ing=ing, steps=steps, tips=notes,
                 video=links_of(doc[i]))
        if with_sauce:
            r["withSauce"] = with_sauce
        if serve:
            r["serve"] = serve
        if sauces:
            r["sauces"] = sauces
        if images and save_image(doc, doc[i], out / "img" / f"{rid}.webp", crop_top=0.36 if not batch else 0.30):
            r["img"] = f"img/{rid}.webp"
        recs.append(r)
    return recs


# ---------- book 2 ----------

B2_SECTIONS = [(5, 101, "main"), (102, 104, "side"), (105, 131, "breakfast"),
               (132, 139, "drink"), (140, 148, "sweet")]


def book2(doc, out, images):
    recs = []
    for i in range(4, 148):
        page = doc[i]
        L = lines_of(page)
        title = join([l["t"] for l in sorted(L, key=lambda l: l["y"]) if "Bingo" in l["font"]])
        if not title:
            continue
        allt = " ".join(l["t"] for l in L)

        def g(pat):
            m = re.search(pat, allt)
            return int(m.group(1)) if m else None
        cal, pro, carb, fat = (g(r"(\d+) ?CALORIES"), g(r"(\d+) ?g PROTEIN"),
                               g(r"(\d+) ?g CARBS"), g(r"(\d+) ?g FAT"))
        heads = sorted([l for l in L if l["size"] >= 15 and "Bingo" not in l["font"]], key=lambda l: l["y"])
        hi = next((h for h in heads if h["t"].lower().startswith("ingredient")), None)
        hm = next((h for h in heads if h["t"].lower().startswith("how to")), None)
        mac = next((l for l in L if l["t"].lower().startswith("macros per")), None)
        ty = max([l["y1"] for l in L if "Bingo" in l["font"]])
        desc = join([l["t"] for l in sorted(L, key=lambda l: l["y"])
                     if l["y"] >= ty - 2 and l["y"] < (mac["y"] if mac else (hi["y"] if hi else ty + 40))
                     and "Bingo" not in l["font"] and l["size"] < 12])
        serves = ""
        ing = []
        if hi:
            sm = re.search(r"\((.*)\)", hi["t"])
            serves = clean(sm.group(1)) if sm else ""
            y0, y1 = hi["y1"] - 2, (hm["y"] - 2 if hm else 800)
            body = [l for l in L if y0 <= l["y"] < y1 and l is not hi]
            marks = [l for l in body if "Wingdings" in l["font"] and len(l["t"]) <= 2]
            txt = [l for l in body if l not in marks and "TAP ICONS" not in l["t"]]
            for l in txt:
                mk = next((m_ for m_ in marks if abs((m_["y"] + m_["y1"]) / 2 - (l["y"] + l["y1"]) / 2) < 6
                           and 0 < l["x"] - m_["x"] < 22), None)
                l["bullet"] = mk is not None
                l["anchor"] = mk["x"] if mk else None
            # column anchors from bullets
            anchors = []
            for a in sorted({round(m_["x"]) for m_ in marks}):
                if not anchors or a - anchors[-1] > 40:
                    anchors.append(a)
            if not anchors:
                anchors = [45]

            def col(l):
                ref = l["anchor"] if l["anchor"] is not None else l["x"]
                best = 0
                for k, a in enumerate(anchors):
                    if ref >= a - 12:
                        best = k
                return best
            for l in txt:
                l["col"] = col(l)
                a = anchors[l["col"]]
                l["header"] = (not l["bullet"]) and l["x"] < a + 4 and (
                    "Regular" in l["font"] or l["t"].endswith(":"))
            seq = sorted(txt, key=lambda l: (l["col"], l["y"]))
            ing = parse_ingredients(seq, dash=False)
        steps, tips = [], []
        if hm:
            body = sorted([l for l in L if l["y"] >= hm["y1"] - 2 and l["y"] < 804 and l is not hm
                           and "Return to" not in l["t"] and not re.fullmatch(r"\d+", l["t"])],
                          key=lambda l: l["y"])
            side = [l for l in body if l["color"] == 0xFFFFFF and l["x"] > 380]
            main = [l for l in body if l not in side and "Wingdings" not in l["font"]]
            cur = None
            for l in main:
                m = re.match(r"^(\d+)\.\s*(.*)", l["t"])
                if m and l["x"] < 60:
                    cur = [m.group(2)]
                    steps.append(cur)
                elif cur is not None:
                    cur.append(l["t"])
                else:
                    cur = [l["t"]]
                    steps.append(cur)
            steps = [join(s) for s in steps]
            cur, last = None, None
            for l in side:
                if last is None or l["y"] - last > 15.5:
                    cur = []
                    tips.append(cur)
                cur.append(l["t"])
                last = l["y"]
            tips = [join(t) for t in tips]
        pg = i + 1
        cat = next(c for a, b, c in B2_SECTIONS if a <= pg <= b)
        rid = f"b{pg:03d}"
        r = dict(id=rid, book=2, page=pg, title=title, cat=cat, cal=cal, pro=pro, carb=carb, fat=fat,
                 serves=serves, desc=desc, ing=ing, steps=steps, tips=tips, video=links_of(page))
        if images and save_image(doc, page, out / "img" / f"{rid}.webp"):
            r["img"] = f"img/{rid}.webp"
        recs.append(r)
    return recs


# ---------- classification ----------

PROTEINS = [
    ("shrimp", r"shrimp|prawn"), ("salmon", r"salmon"), ("tuna", r"tuna"),
    ("steak", r"steak|sirloin|topside|rump|beef strips|flank"),
    ("ground-beef", r"ground beef|beef mince|minced beef|mince\b|lean beef|burger patt"),
    ("chicken-thigh", r"chicken thigh"), ("chicken-breast", r"chicken breast|chicken tender|chicken mince|ground chicken|chicken wing|whole chicken|raw chicken|chicken"),
    ("turkey", r"turkey"), ("eggs", r"\begg"),
]
CARBS = [("rice", r"\brice\b"), ("pasta", r"pasta|macaroni|penne|spaghetti|linguine|fettuccine|lasagn|rigatoni|fusilli"),
         ("noodles", r"noodle"), ("potato", r"potato|fries|chips\b"),
         ("bread", r"tortilla|wrap|bun\b|buns|naan|bread|pita|bagel|toast|pizza|taco|quesadilla|burrito|sandwich|burger"),
         ("oats", r"\boats?\b")]
FLAVOURS = [
    ("korean", r"korean|gochujang|bulgogi|kimchi"), ("mexican", r"taco|fajita|burrito|chipotle|mexican|nacho|quesadilla|street corn|chilli lime|salsa"),
    ("indian", r"butter chicken|tikka|tandoori|biryani|masala|curry\b"),
    ("middle-eastern", r"shawarma|kebab|gyro|halal cart|sumac|turkish|middle eastern|kofta"),
    ("asian", r"teriyaki|orange chicken|sesame|pad thai|chow mein|fried rice|stir fry|mongolian|bang bang|soy sauce|sweet (and|n|&) sour|thai|noodle|katsu|yum yum"),
    ("italian", r"alfredo|tuscan|bolognes|lasagn|parm|pesto|pizza|marinara|linguine|spaghetti"),
    ("bbq-buffalo", r"bbq|buffalo|peri peri|cajun|hot sauce|nashville|wings"),
    ("creamy", r"creamy|mac n cheese|mac & cheese|mac and cheese|cheesy|alfredo"),
    ("sweet-heat", r"honey|sticky|sweet chilli|mango habanero|sriracha"),
]


def classify(r):
    title = r["title"].lower()
    ings = " | ".join(x for g in r["ing"] for x in g["items"]).lower()
    need = []
    for g in r["ing"]:
        for item in g["items"]:
            c = canon_for(item)
            if c and c not in need:
                need.append(c)
    r["need"] = need
    r["ic"] = [[canon_for(it) or "" for it in g["items"]] for g in r["ing"]]
    pmap = {"chicken-breast": "chicken-breast", "chicken-wings": "chicken-breast", "whole-chicken": "chicken-breast",
            "chicken-mince": "chicken-breast", "chicken-thigh": "chicken-thigh", "steak": "steak",
            "ground-beef": "ground-beef", "shrimp": "shrimp", "salmon": "salmon", "tuna": "tuna"}
    prot = []
    for c in need:
        if c in pmap and pmap[c] not in prot:
            prot.append(pmap[c])
    if not prot and "chicken" in title:
        prot.append("chicken-breast")
    if not prot and r["cat"] not in ("sweet", "drink"):
        if "eggs" in need or "egg-whites" in need:
            prot.append("eggs")
    r["protein"] = prot
    carbs = [k for k, pat in CARBS if re.search(pat, title + " | " + ings)]
    r["carbs"] = carbs
    r["flavour"] = [k for k, pat in FLAVOURS if re.search(pat, title + " | " + ings if k in ("korean",) else title)]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    images = "--no-images" not in sys.argv
    p1, p2, out = args[0], args[1], Path(args[2])
    (out / "img").mkdir(parents=True, exist_ok=True)
    recs = book1(pymupdf.open(p1), out, images) + book2(pymupdf.open(p2), out, images)
    for r in recs:
        classify(r)
    payload = dict(recipes=recs, canon=[dict(id=k, name=v[0], kind=v[1], aisle=v[2]) for k, v in CANON.items()])
    (out / "recipes.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    print(len(recs), "recipes ->", out / "recipes.json", (out / "recipes.json").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
