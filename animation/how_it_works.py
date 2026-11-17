"""
Explainer animation for the How it works page (Manim). Silent, about 30 s.

    python -m manim -qm how_it_works.py HowItWorks

Uses the real result of the Datejust sample photo (probabilities and variants from
front_end/src/data/examples.json). Colours match the site; the font is Georgia.
"""
import json
from pathlib import Path

from manim import *

ROOT = Path(__file__).parent
BG, INK, GREEN, GOLD, GREY, LINE = "#F6F2E8", "#1E1E1E", "#0B2F23", "#C9A348", "#6b7b74", "#DED8CA"
FONT = "Georgia"  # Tienne (the site font) renders broken glyphs in Manim; Georgia is the closest serif
config.background_color = BG

_examples = json.loads((ROOT.parent / "front_end/src/data/examples.json").read_text(encoding="utf-8"))
EXAMPLE = next(e for e in _examples if e["id"] == "datejust")["result"]
NAMES = {
    "datejust": "Datejust", "turn_o_graph": "Turn-O-Graph", "explorer": "Explorer",
    "oysterquartz": "Oysterquartz", "president": "President", "daytona": "Daytona",
}


def T(text, size=30, color=INK, bold=False):
    return Text(text, font=FONT, font_size=size, color=color, weight=BOLD if bold else NORMAL)


def caption(step, text):
    number = T(str(step), 30, GOLD, True)
    label = T(text, 30, GREEN)
    group = VGroup(number, label).arrange(RIGHT, buff=0.3)
    group.move_to(DOWN * 3.3)
    return group


class HowItWorks(Scene):
    def construct(self):
        self.play_all()

    def play_all(self):
        # ---------- title ----------
        title = T("How a photo becomes an answer", 44, INK)
        rule = Line(LEFT * 3, RIGHT * 3, color=GOLD, stroke_width=2).next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(title, shift=UP * 0.2), Create(rule), run_time=1.2)
        self.wait(1.0)
        self.play(FadeOut(title), FadeOut(rule), run_time=0.6)

        # ---------- 1. find the watch ----------
        k = 4.8 / 480
        photo = ImageMobject(str(ROOT / "assets/photo.jpg")).set_height(4.8).move_to(UP * 0.3)

        def px(x, y):
            return photo.get_center() + np.array([(x - 320) * k, -(y - 240) * k, 0])

        credit = T("Photo: ajay_suresh, CC BY 2.0, Wikimedia Commons", 16, GREY)
        credit.next_to(photo, DOWN, buff=0.12).align_to(photo, RIGHT)
        self.play(FadeIn(photo), FadeIn(credit), run_time=0.8)
        cap = caption(1, "Find the watch")
        self.play(FadeIn(cap, shift=UP * 0.15), run_time=0.5)
        box = Rectangle(width=(500 - 165) * k, height=(475 - 5) * k, color=GOLD, stroke_width=5).move_to(px(332.5, 240))
        tag = T("watch", 22, GREEN, True)
        tag.next_to(box, RIGHT, buff=0.25).align_to(box, UP)
        self.play(Create(box), run_time=1.2)
        self.play(FadeIn(tag), run_time=0.4)
        self.wait(1.0)

        # ---------- 2. crop the dial ----------
        cap2 = caption(2, "Crop the dial")
        self.play(ReplacementTransform(cap, cap2), FadeOut(tag), run_time=0.5)
        dial_box = Square(side_length=300 * k, color=GOLD, stroke_width=5).move_to(px(322, 232))
        self.play(ReplacementTransform(box, dial_box), run_time=1.0)
        self.wait(0.4)
        dial = ImageMobject(str(ROOT / "assets/dial.png")).set_height(300 * k).move_to(px(322, 232))
        self.add(dial, dial_box)
        self.play(FadeOut(photo), FadeOut(credit), FadeOut(dial_box),
                  dial.animate.set_height(2.6).move_to(LEFT * 4.9 + UP * 0.6), run_time=1.2)
        self.wait(0.3)

        # ---------- 3. numbers ----------
        cap3 = caption(3, "Turn it into numbers")
        self.play(ReplacementTransform(cap2, cap3), run_time=0.5)
        clip = VGroup(
            RoundedRectangle(corner_radius=0.05, width=2.6, height=1.3, color=GREEN, stroke_width=3,
                             fill_color=GREEN, fill_opacity=1),
            T("CLIP", 30, BG, True),
        )
        clip[1].move_to(clip[0])
        clip.move_to(LEFT * 1.3 + UP * 0.6)
        arrow1 = Arrow(dial.get_right() + RIGHT * 0.1, clip.get_left() + LEFT * 0.05, color=GOLD, buff=0.1, stroke_width=4)
        self.play(Create(arrow1), FadeIn(clip), run_time=0.8)
        values = ["0.12", "-0.48", "0.31", "0.05", "-0.27", "0.66", "..."]
        nums = VGroup(*[T(v, 26, GREEN) for v in values]).arrange(RIGHT, buff=0.35)
        nums.move_to(RIGHT * 3.6 + UP * 0.6)
        arrow2 = Arrow(clip.get_right() + RIGHT * 0.05, nums.get_left() + LEFT * 0.2, color=GOLD, buff=0.1, stroke_width=4)
        brace = Brace(nums, DOWN, color=GREY, buff=0.15)
        brace_label = T("512 numbers", 24, GREY).next_to(brace, DOWN, buff=0.15)
        self.play(Create(arrow2), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(n, shift=RIGHT * 0.15) for n in nums], lag_ratio=0.12), run_time=1.4)
        self.play(GrowFromCenter(brace), FadeIn(brace_label), run_time=0.6)
        self.wait(1.2)

        # ---------- 4. pick the family ----------
        cap4 = caption(4, "Pick the family")
        small = nums.copy().scale(0.8).move_to(UP * 2.9)
        self.play(
            ReplacementTransform(cap3, cap4),
            FadeOut(dial), FadeOut(clip), FadeOut(arrow1), FadeOut(arrow2), FadeOut(brace), FadeOut(brace_label),
            ReplacementTransform(nums, small),
            run_time=1.0,
        )
        layer = VGroup(
            RoundedRectangle(corner_radius=0.05, width=3.6, height=0.7, color=GOLD, stroke_width=3),
            T("trained layer", 24, GREEN),
        )
        layer[1].move_to(layer[0])
        layer.move_to(UP * 1.9)
        down = Arrow(small.get_bottom(), layer.get_top(), color=GOLD, buff=0.08, stroke_width=3,
                     max_tip_length_to_length_ratio=0.3)
        self.play(Create(down), FadeIn(layer), run_time=0.7)

        probs = sorted(EXAMPLE["probabilities"].items(), key=lambda kv: -kv[1])[:6]
        rows = VGroup()
        x0 = -2.0
        for i, (name, p) in enumerate(probs):
            label = T(NAMES.get(name, name), 26, INK if i == 0 else GREY, i == 0)
            label.move_to(np.array([x0 - 0.2, 0.7 - i * 0.52, 0]), aligned_edge=RIGHT)
            width = max(0.04, 5.6 * p)
            bar = Rectangle(width=width, height=0.3, stroke_width=0,
                            fill_color=GOLD if i == 0 else GREEN, fill_opacity=1 if i == 0 else 0.35)
            bar.move_to(np.array([x0 + 0.1, label.get_center()[1], 0]), aligned_edge=LEFT)
            pct = T(f"{p * 100:.0f}%" if p >= 0.1 else f"{p * 100:.1f}%", 22, INK if i == 0 else GREY)
            pct.next_to(bar, RIGHT, buff=0.2)
            rows.add(VGroup(label, bar, pct))
        arrow_to_bars = Arrow(layer.get_bottom(), UP * 1.15, color=GOLD, buff=0.08, stroke_width=3,
                              max_tip_length_to_length_ratio=0.3)
        self.play(Create(arrow_to_bars), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(r[0]) for r in rows], lag_ratio=0.08), run_time=0.8)
        self.play(LaggedStart(*[GrowFromEdge(r[1], LEFT) for r in rows], lag_ratio=0.1), run_time=1.6)
        self.play(LaggedStart(*[FadeIn(r[2]) for r in rows], lag_ratio=0.08), run_time=0.6)
        more = T("14 families in all", 20, GREY).move_to(DOWN * 2.25)
        self.play(FadeIn(more), run_time=0.4)
        self.wait(1.4)

        # ---------- 5. closest variants ----------
        cap5 = caption(5, "Find the closest variants")
        head = T("Datejust", 56, INK).move_to(UP * 2.5 + LEFT * 4.7, aligned_edge=LEFT)
        rule2 = Line(LEFT * 6.2, RIGHT * 6.2, color=LINE, stroke_width=2).move_to(UP * 1.7)
        self.play(
            ReplacementTransform(cap4, cap5),
            FadeOut(rows), FadeOut(small), FadeOut(down), FadeOut(layer), FadeOut(arrow_to_bars), FadeOut(more),
            FadeIn(head), Create(rule2), run_time=1.0,
        )
        variants = VGroup()
        for i, c in enumerate(EXAMPLE["variant_candidates"][:3]):
            name = T(c["display_name"], 36 if i == 0 else 30, INK if i == 0 else GREEN)
            refs = T("Reference  " + "   ".join(c["reference_examples"][:4]), 22, GREY)
            variants.add(VGroup(name, refs).arrange(DOWN, aligned_edge=LEFT, buff=0.12))
        variants.arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to(LEFT * 4.7 + DOWN * 0.4, aligned_edge=LEFT)
        best = T("Best match", 20, GOLD, True).next_to(variants[0][0], RIGHT, buff=0.35)
        self.play(LaggedStart(*[FadeIn(v, shift=UP * 0.2) for v in variants], lag_ratio=0.35), run_time=2.2)
        self.play(FadeIn(best), run_time=0.4)
        self.wait(1.8)

        # ---------- close ----------
        end = T("A close estimate, not a guarantee.", 32, GREEN).move_to(DOWN * 3.3)
        self.play(FadeOut(cap5), FadeIn(end), run_time=0.8)
        self.wait(2.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
