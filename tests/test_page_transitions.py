"""Tests for page_transitions module (Feature 60)."""

import pytest
from oxidize_pdf import (
    TransitionStyle,
    TransitionDimension,
    TransitionMotion,
    TransitionDirection,
    PageTransition,
)


# ── TransitionStyle ────────────────────────────────────────────────────────


class TestTransitionStyle:
    def test_all_twelve_variants_exist(self):
        variants = [
            TransitionStyle.SPLIT,
            TransitionStyle.BLINDS,
            TransitionStyle.BOX,
            TransitionStyle.WIPE,
            TransitionStyle.DISSOLVE,
            TransitionStyle.GLITTER,
            TransitionStyle.REPLACE,
            TransitionStyle.FLY,
            TransitionStyle.PUSH,
            TransitionStyle.COVER,
            TransitionStyle.UNCOVER,
            TransitionStyle.FADE,
        ]
        assert len(variants) == 12

    def test_repr_split(self):
        assert repr(TransitionStyle.SPLIT) == "TransitionStyle.SPLIT"

    def test_repr_blinds(self):
        assert repr(TransitionStyle.BLINDS) == "TransitionStyle.BLINDS"

    def test_repr_box(self):
        assert repr(TransitionStyle.BOX) == "TransitionStyle.BOX"

    def test_repr_wipe(self):
        assert repr(TransitionStyle.WIPE) == "TransitionStyle.WIPE"

    def test_repr_dissolve(self):
        assert repr(TransitionStyle.DISSOLVE) == "TransitionStyle.DISSOLVE"

    def test_repr_glitter(self):
        assert repr(TransitionStyle.GLITTER) == "TransitionStyle.GLITTER"

    def test_repr_replace(self):
        assert repr(TransitionStyle.REPLACE) == "TransitionStyle.REPLACE"

    def test_repr_fly(self):
        assert repr(TransitionStyle.FLY) == "TransitionStyle.FLY"

    def test_repr_push(self):
        assert repr(TransitionStyle.PUSH) == "TransitionStyle.PUSH"

    def test_repr_cover(self):
        assert repr(TransitionStyle.COVER) == "TransitionStyle.COVER"

    def test_repr_uncover(self):
        assert repr(TransitionStyle.UNCOVER) == "TransitionStyle.UNCOVER"

    def test_repr_fade(self):
        assert repr(TransitionStyle.FADE) == "TransitionStyle.FADE"


# ── TransitionDimension ────────────────────────────────────────────────────


class TestTransitionDimension:
    def test_horizontal_exists(self):
        assert TransitionDimension.HORIZONTAL is not None

    def test_vertical_exists(self):
        assert TransitionDimension.VERTICAL is not None

    def test_repr_horizontal(self):
        assert repr(TransitionDimension.HORIZONTAL) == "TransitionDimension.HORIZONTAL"

    def test_repr_vertical(self):
        assert repr(TransitionDimension.VERTICAL) == "TransitionDimension.VERTICAL"


# ── TransitionMotion ───────────────────────────────────────────────────────


class TestTransitionMotion:
    def test_inward_exists(self):
        assert TransitionMotion.INWARD is not None

    def test_outward_exists(self):
        assert TransitionMotion.OUTWARD is not None

    def test_repr_inward(self):
        assert repr(TransitionMotion.INWARD) == "TransitionMotion.INWARD"

    def test_repr_outward(self):
        assert repr(TransitionMotion.OUTWARD) == "TransitionMotion.OUTWARD"


# ── TransitionDirection ────────────────────────────────────────────────────


class TestTransitionDirection:
    def test_left_to_right_exists(self):
        assert TransitionDirection.LEFT_TO_RIGHT is not None

    def test_bottom_to_top_exists(self):
        assert TransitionDirection.BOTTOM_TO_TOP is not None

    def test_right_to_left_exists(self):
        assert TransitionDirection.RIGHT_TO_LEFT is not None

    def test_top_to_bottom_exists(self):
        assert TransitionDirection.TOP_TO_BOTTOM is not None

    def test_top_left_to_bottom_right_exists(self):
        assert TransitionDirection.TOP_LEFT_TO_BOTTOM_RIGHT is not None

    def test_custom_static_method(self):
        custom = TransitionDirection.custom(45)
        assert custom is not None

    def test_custom_repr(self):
        custom = TransitionDirection.custom(90)
        assert "90" in repr(custom)

    def test_repr_left_to_right(self):
        assert repr(TransitionDirection.LEFT_TO_RIGHT) == "TransitionDirection.LEFT_TO_RIGHT"

    def test_repr_bottom_to_top(self):
        assert repr(TransitionDirection.BOTTOM_TO_TOP) == "TransitionDirection.BOTTOM_TO_TOP"

    def test_repr_right_to_left(self):
        assert repr(TransitionDirection.RIGHT_TO_LEFT) == "TransitionDirection.RIGHT_TO_LEFT"

    def test_repr_top_to_bottom(self):
        assert repr(TransitionDirection.TOP_TO_BOTTOM) == "TransitionDirection.TOP_TO_BOTTOM"

    def test_repr_top_left_to_bottom_right(self):
        assert (
            repr(TransitionDirection.TOP_LEFT_TO_BOTTOM_RIGHT)
            == "TransitionDirection.TOP_LEFT_TO_BOTTOM_RIGHT"
        )


# ── PageTransition ─────────────────────────────────────────────────────────


class TestPageTransitionNew:
    def test_new_with_style(self):
        t = PageTransition(TransitionStyle.DISSOLVE)
        assert t is not None

    def test_repr_includes_style(self):
        t = PageTransition(TransitionStyle.FADE)
        assert "FADE" in repr(t)

    def test_new_with_each_style(self):
        for style in [
            TransitionStyle.SPLIT,
            TransitionStyle.BLINDS,
            TransitionStyle.BOX,
            TransitionStyle.WIPE,
            TransitionStyle.DISSOLVE,
            TransitionStyle.GLITTER,
            TransitionStyle.REPLACE,
            TransitionStyle.FLY,
            TransitionStyle.PUSH,
            TransitionStyle.COVER,
            TransitionStyle.UNCOVER,
            TransitionStyle.FADE,
        ]:
            t = PageTransition(style)
            assert t is not None


class TestPageTransitionBuilders:
    def test_with_duration(self):
        t = PageTransition(TransitionStyle.DISSOLVE).with_duration(2.5)
        assert t is not None

    def test_with_duration_returns_new_instance(self):
        base = PageTransition(TransitionStyle.DISSOLVE)
        modified = base.with_duration(1.0)
        assert modified is not base

    def test_with_dimension(self):
        t = PageTransition(TransitionStyle.SPLIT).with_dimension(TransitionDimension.HORIZONTAL)
        assert t is not None

    def test_with_motion(self):
        t = PageTransition(TransitionStyle.SPLIT).with_motion(TransitionMotion.INWARD)
        assert t is not None

    def test_with_direction(self):
        t = PageTransition(TransitionStyle.WIPE).with_direction(
            TransitionDirection.LEFT_TO_RIGHT
        )
        assert t is not None

    def test_with_scale(self):
        t = PageTransition(TransitionStyle.FLY).with_scale(1.5)
        assert t is not None

    def test_with_area(self):
        t = PageTransition(TransitionStyle.FLY).with_area(10.0, 20.0, 100.0, 200.0)
        assert t is not None

    def test_chained_builders(self):
        t = (
            PageTransition(TransitionStyle.FLY)
            .with_duration(1.5)
            .with_direction(TransitionDirection.BOTTOM_TO_TOP)
            .with_scale(1.2)
            .with_area(0.0, 0.0, 200.0, 300.0)
        )
        assert t is not None

    def test_with_direction_custom(self):
        t = PageTransition(TransitionStyle.GLITTER).with_direction(
            TransitionDirection.custom(45)
        )
        assert t is not None


class TestPageTransitionConvenienceConstructors:
    def test_split(self):
        t = PageTransition.split(TransitionDimension.HORIZONTAL, TransitionMotion.INWARD)
        assert "SPLIT" in repr(t)

    def test_split_vertical_outward(self):
        t = PageTransition.split(TransitionDimension.VERTICAL, TransitionMotion.OUTWARD)
        assert t is not None

    def test_blinds(self):
        t = PageTransition.blinds(TransitionDimension.HORIZONTAL)
        assert "BLINDS" in repr(t)

    def test_blinds_vertical(self):
        t = PageTransition.blinds(TransitionDimension.VERTICAL)
        assert t is not None

    def test_box_transition(self):
        t = PageTransition.box_transition(TransitionMotion.INWARD)
        assert "BOX" in repr(t)

    def test_box_transition_outward(self):
        t = PageTransition.box_transition(TransitionMotion.OUTWARD)
        assert t is not None

    def test_wipe(self):
        t = PageTransition.wipe(TransitionDirection.LEFT_TO_RIGHT)
        assert "WIPE" in repr(t)

    def test_dissolve(self):
        t = PageTransition.dissolve()
        assert "DISSOLVE" in repr(t)

    def test_glitter(self):
        t = PageTransition.glitter(TransitionDirection.TOP_TO_BOTTOM)
        assert "GLITTER" in repr(t)

    def test_replace(self):
        t = PageTransition.replace()
        assert "REPLACE" in repr(t)

    def test_fly(self):
        t = PageTransition.fly(TransitionDirection.BOTTOM_TO_TOP)
        assert "FLY" in repr(t)

    def test_push(self):
        t = PageTransition.push(TransitionDirection.RIGHT_TO_LEFT)
        assert "PUSH" in repr(t)

    def test_cover(self):
        t = PageTransition.cover(TransitionDirection.TOP_TO_BOTTOM)
        assert "COVER" in repr(t)

    def test_uncover(self):
        t = PageTransition.uncover(TransitionDirection.LEFT_TO_RIGHT)
        assert "UNCOVER" in repr(t)

    def test_fade(self):
        t = PageTransition.fade()
        assert "FADE" in repr(t)

    def test_convenience_constructors_with_duration(self):
        t = PageTransition.dissolve().with_duration(3.0)
        assert t is not None

    def test_fly_with_all_options(self):
        t = (
            PageTransition.fly(TransitionDirection.custom(45))
            .with_duration(2.0)
            .with_scale(1.0)
            .with_area(0.0, 0.0, 612.0, 792.0)
        )
        assert t is not None

    def test_wipe_with_custom_direction(self):
        t = PageTransition.wipe(TransitionDirection.custom(135))
        assert t is not None
