"""Tests for advanced graphics module (Tier 13, F65-F70)."""

import pytest
import oxidize_pdf as ox


# ── F65: Shadings ────────────────────────────────────────────────────────────


class TestShadingType:
    def test_variants_exist(self):
        assert ox.ShadingType.FUNCTION_BASED is not None
        assert ox.ShadingType.AXIAL is not None
        assert ox.ShadingType.RADIAL is not None
        assert ox.ShadingType.FREE_FORM_GOURAUD is not None
        assert ox.ShadingType.LATTICE_FORM_GOURAUD is not None
        assert ox.ShadingType.COONS_PATCH is not None
        assert ox.ShadingType.TENSOR_PRODUCT_PATCH is not None

    def test_repr(self):
        assert "AXIAL" in repr(ox.ShadingType.AXIAL)
        assert "RADIAL" in repr(ox.ShadingType.RADIAL)


class TestShadingPoint:
    def test_constructor(self):
        p = ox.ShadingPoint(10.0, 20.0)
        assert p.x == 10.0
        assert p.y == 20.0

    def test_repr(self):
        p = ox.ShadingPoint(3.0, 4.0)
        r = repr(p)
        assert "3" in r
        assert "4" in r


class TestColorStop:
    def test_constructor(self):
        stop = ox.ColorStop(0.5, ox.Color.red())
        assert stop.position == 0.5

    def test_clamping(self):
        # Positions outside [0,1] should be clamped
        stop = ox.ColorStop(1.5, ox.Color.blue())
        assert stop.position == 1.0


class TestAxialShading:
    def test_linear_gradient_factory(self):
        start = ox.ShadingPoint(0.0, 0.0)
        end = ox.ShadingPoint(100.0, 0.0)
        shading = ox.AxialShading.linear_gradient(
            "TestGrad", start, end, ox.Color.red(), ox.Color.blue()
        )
        assert shading.name == "TestGrad"
        assert not shading.extend_start
        assert not shading.extend_end

    def test_with_extend(self):
        start = ox.ShadingPoint(0.0, 0.0)
        end = ox.ShadingPoint(100.0, 0.0)
        shading = ox.AxialShading.linear_gradient(
            "ExtGrad", start, end, ox.Color.red(), ox.Color.blue()
        ).with_extend(True, True)
        assert shading.extend_start
        assert shading.extend_end

    def test_constructor_with_stops(self):
        start = ox.ShadingPoint(0.0, 0.0)
        end = ox.ShadingPoint(100.0, 0.0)
        stops = [ox.ColorStop(0.0, ox.Color.red()), ox.ColorStop(1.0, ox.Color.blue())]
        shading = ox.AxialShading("MyGrad", start, end, stops)
        assert shading.name == "MyGrad"

    def test_validate_valid(self):
        start = ox.ShadingPoint(0.0, 0.0)
        end = ox.ShadingPoint(100.0, 0.0)
        shading = ox.AxialShading.linear_gradient(
            "Valid", start, end, ox.Color.red(), ox.Color.blue()
        )
        shading.validate()  # Should not raise

    def test_repr(self):
        start = ox.ShadingPoint(0.0, 0.0)
        end = ox.ShadingPoint(10.0, 0.0)
        s = ox.AxialShading.linear_gradient("X", start, end, ox.Color.red(), ox.Color.blue())
        assert "AxialShading" in repr(s)


class TestRadialShading:
    def test_radial_gradient_factory(self):
        center = ox.ShadingPoint(50.0, 50.0)
        shading = ox.RadialShading.radial_gradient(
            "RadGrad", center, 0.0, 25.0, ox.Color.white(), ox.Color.black()
        )
        assert shading.name == "RadGrad"
        assert shading.start_radius == 0.0
        assert shading.end_radius == 25.0

    def test_with_extend(self):
        center = ox.ShadingPoint(50.0, 50.0)
        shading = ox.RadialShading.radial_gradient(
            "Ext", center, 0.0, 25.0, ox.Color.red(), ox.Color.blue()
        ).with_extend(True, False)
        # Verify builder returns valid object (extend fields not exposed as Python props)
        assert shading is not None
        assert shading.name == "Ext"

    def test_constructor_with_stops(self):
        center = ox.ShadingPoint(50.0, 50.0)
        stops = [ox.ColorStop(0.0, ox.Color.red()), ox.ColorStop(1.0, ox.Color.blue())]
        shading = ox.RadialShading("RadGrad2", center, 0.0, center, 50.0, stops)
        assert shading.name == "RadGrad2"

    def test_validate_valid(self):
        center = ox.ShadingPoint(50.0, 50.0)
        shading = ox.RadialShading.radial_gradient(
            "Valid", center, 0.0, 25.0, ox.Color.red(), ox.Color.blue()
        )
        shading.validate()  # Should not raise


class TestShadingManager:
    def test_new_empty(self):
        m = ox.ShadingManager()
        assert m.shading_count() == 0

    def test_create_linear_gradient(self):
        m = ox.ShadingManager()
        name = m.create_linear_gradient(
            ox.ShadingPoint(0.0, 0.0),
            ox.ShadingPoint(100.0, 0.0),
            ox.Color.red(),
            ox.Color.blue(),
        )
        assert isinstance(name, str)
        assert m.shading_count() == 1

    def test_create_radial_gradient(self):
        m = ox.ShadingManager()
        name = m.create_radial_gradient(
            ox.ShadingPoint(50.0, 50.0),
            0.0,
            25.0,
            ox.Color.white(),
            ox.Color.black(),
        )
        assert isinstance(name, str)
        assert m.shading_count() == 1

    def test_add_axial(self):
        m = ox.ShadingManager()
        start = ox.ShadingPoint(0.0, 0.0)
        end = ox.ShadingPoint(100.0, 0.0)
        shading = ox.AxialShading.linear_gradient("G1", start, end, ox.Color.red(), ox.Color.blue())
        name = m.add_axial_shading(shading)
        assert name == "G1"
        assert m.shading_count() == 1

    def test_clear(self):
        m = ox.ShadingManager()
        m.create_linear_gradient(
            ox.ShadingPoint(0.0, 0.0),
            ox.ShadingPoint(100.0, 0.0),
            ox.Color.red(),
            ox.Color.blue(),
        )
        assert m.shading_count() == 1
        m.clear()
        assert m.shading_count() == 0


# ── F66: Patterns ────────────────────────────────────────────────────────────


class TestPaintType:
    def test_variants(self):
        assert ox.PaintType.COLORED is not None
        assert ox.PaintType.UNCOLORED is not None

    def test_repr(self):
        assert "COLORED" in repr(ox.PaintType.COLORED)


class TestTilingType:
    def test_variants(self):
        assert ox.TilingType.CONSTANT_SPACING is not None
        assert ox.TilingType.NO_DISTORTION is not None
        assert ox.TilingType.CONSTANT_SPACING_FASTER is not None

    def test_repr(self):
        assert "NO_DISTORTION" in repr(ox.TilingType.NO_DISTORTION)


class TestPatternMatrix:
    def test_identity(self):
        m = ox.PatternMatrix.identity()
        assert list(m.matrix) == [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

    def test_translation(self):
        m = ox.PatternMatrix.translation(10.0, 20.0)
        assert list(m.matrix) == [1.0, 0.0, 0.0, 1.0, 10.0, 20.0]

    def test_scale(self):
        m = ox.PatternMatrix.scale(2.0, 3.0)
        assert list(m.matrix) == [2.0, 0.0, 0.0, 3.0, 0.0, 0.0]

    def test_rotation(self):
        import math
        m = ox.PatternMatrix.rotation(math.pi / 2)
        assert abs(m.matrix[0]) < 1e-10  # cos(90°) ≈ 0
        assert abs(m.matrix[1] - 1.0) < 1e-10  # sin(90°) ≈ 1

    def test_multiply(self):
        t = ox.PatternMatrix.translation(10.0, 20.0)
        s = ox.PatternMatrix.scale(2.0, 3.0)
        result = t.multiply(s)
        assert list(result.matrix) == [2.0, 0.0, 0.0, 3.0, 20.0, 60.0]


class TestTilingPattern:
    def test_constructor(self):
        p = ox.TilingPattern(
            "TestPattern",
            ox.PaintType.COLORED,
            ox.TilingType.CONSTANT_SPACING,
            [0.0, 0.0, 100.0, 100.0],
            50.0,
            50.0,
        )
        assert p.name == "TestPattern"
        assert p.x_step == 50.0
        assert p.y_step == 50.0

    def test_with_matrix(self):
        p = ox.TilingPattern(
            "P2", ox.PaintType.COLORED, ox.TilingType.CONSTANT_SPACING,
            [0.0, 0.0, 100.0, 100.0], 50.0, 50.0,
        )
        m = ox.PatternMatrix.scale(2.0, 2.0)
        p2 = p.with_matrix(m)
        # with_matrix returns a new TilingPattern with the matrix applied
        assert p2 is not None
        assert p2.name == "P2"

    def test_add_operations(self):
        p = ox.TilingPattern(
            "DrawP", ox.PaintType.COLORED, ox.TilingType.CONSTANT_SPACING,
            [0.0, 0.0, 100.0, 100.0], 50.0, 50.0,
        )
        p.add_rectangle(10.0, 10.0, 50.0, 50.0)
        p.fill()
        p.add_line(0.0, 0.0, 50.0, 50.0)
        p.stroke()
        p.add_circle(50.0, 50.0, 20.0)
        p.fill_and_stroke()


class TestPatternManager:
    def test_new_empty(self):
        m = ox.PatternManager()
        assert m.count() == 0

    def test_create_checkerboard(self):
        m = ox.PatternManager()
        name = m.create_checkerboard_pattern(25.0, [1.0, 0.0, 0.0], [0.0, 0.0, 1.0])
        assert isinstance(name, str)
        assert m.count() == 1

    def test_create_stripe(self):
        m = ox.PatternManager()
        name = m.create_stripe_pattern(10.0, 45.0, [0.0, 1.0, 0.0], [1.0, 1.0, 0.0])
        assert isinstance(name, str)
        assert m.count() == 1

    def test_create_dots(self):
        m = ox.PatternManager()
        name = m.create_dots_pattern(5.0, 20.0, [1.0, 0.0, 1.0], [1.0, 1.0, 1.0])
        assert isinstance(name, str)
        assert m.count() == 1

    def test_clear(self):
        m = ox.PatternManager()
        m.create_checkerboard_pattern(10.0, [1.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        assert m.count() == 1
        m.clear()
        assert m.count() == 0


# ── F67: FormXObject ─────────────────────────────────────────────────────────


class TestFormXObject:
    def test_constructor(self):
        bbox = ox.Rectangle.from_xywh(0.0, 0.0, 100.0, 100.0)
        form = ox.FormXObject(bbox)
        assert not form.has_transparency()

    def test_with_matrix(self):
        bbox = ox.Rectangle.from_xywh(0.0, 0.0, 100.0, 100.0)
        form = ox.FormXObject(bbox).with_matrix([2.0, 0.0, 0.0, 2.0, 10.0, 10.0])
        assert not form.has_transparency()

    def test_from_graphics_ops(self):
        bbox = ox.Rectangle.from_xywh(0.0, 0.0, 100.0, 100.0)
        form = ox.FormXObject.from_graphics_ops(bbox, "0 0 100 100 re f")
        assert not form.has_transparency()

    def test_repr(self):
        bbox = ox.Rectangle.from_xywh(0.0, 0.0, 50.0, 50.0)
        form = ox.FormXObject(bbox)
        assert "FormXObject" in repr(form)


class TestFormXObjectBuilder:
    def test_basic_build(self):
        bbox = ox.Rectangle.from_xywh(0.0, 0.0, 100.0, 100.0)
        builder = ox.FormXObjectBuilder(bbox)
        builder.fill_color(1.0, 0.0, 0.0)
        builder.rectangle(10.0, 10.0, 80.0, 80.0)
        builder.fill()
        form = builder.build()
        assert isinstance(form, ox.FormXObject)

    def test_chain_operations(self):
        bbox = ox.Rectangle.from_xywh(0.0, 0.0, 200.0, 200.0)
        builder = ox.FormXObjectBuilder(bbox)
        builder.save_state()
        builder.stroke_color(0.0, 0.0, 1.0)
        builder.move_to(50.0, 50.0)
        builder.line_to(150.0, 150.0)
        builder.stroke()
        builder.restore_state()
        builder.transparency_group(True, False)
        form = builder.build()
        assert form.has_transparency()

    def test_consumed_raises(self):
        bbox = ox.Rectangle.from_xywh(0.0, 0.0, 100.0, 100.0)
        builder = ox.FormXObjectBuilder(bbox)
        builder.fill()
        builder.build()
        with pytest.raises(RuntimeError):
            builder.build()


class TestFormTemplates:
    def test_checkmark(self):
        form = ox.FormTemplates.checkmark(20.0)
        assert isinstance(form, ox.FormXObject)

    def test_cross(self):
        form = ox.FormTemplates.cross(30.0)
        assert isinstance(form, ox.FormXObject)

    def test_circle_filled(self):
        form = ox.FormTemplates.circle(25.0, True)
        assert isinstance(form, ox.FormXObject)

    def test_circle_stroked(self):
        form = ox.FormTemplates.circle(25.0, False)
        assert isinstance(form, ox.FormXObject)

    def test_star(self):
        form = ox.FormTemplates.star(100.0, 5)
        assert isinstance(form, ox.FormXObject)

    def test_logo_placeholder(self):
        form = ox.FormTemplates.logo_placeholder(200.0, 100.0)
        assert isinstance(form, ox.FormXObject)


class TestFormXObjectManager:
    def test_new_empty(self):
        m = ox.FormXObjectManager()
        assert m.count() == 0

    def test_add_and_get(self):
        m = ox.FormXObjectManager()
        bbox = ox.Rectangle.from_xywh(0.0, 0.0, 50.0, 50.0)
        form = ox.FormXObject(bbox)
        name = m.add_form("MyForm", form)
        assert name == "MyForm"
        assert m.count() == 1
        retrieved = m.get_form("MyForm")
        assert retrieved is not None

    def test_auto_name(self):
        m = ox.FormXObjectManager()
        bbox = ox.Rectangle.from_xywh(0.0, 0.0, 50.0, 50.0)
        form = ox.FormXObject(bbox)
        name = m.add_form(None, form)
        assert name.startswith("Fm")

    def test_remove(self):
        m = ox.FormXObjectManager()
        bbox = ox.Rectangle.from_xywh(0.0, 0.0, 50.0, 50.0)
        form = ox.FormXObject(bbox)
        m.add_form("F1", form)
        assert m.count() == 1
        result = m.remove_form("F1")
        assert result is True
        assert m.count() == 0

    def test_clear(self):
        m = ox.FormXObjectManager()
        bbox = ox.Rectangle.from_xywh(0.0, 0.0, 50.0, 50.0)
        form = ox.FormXObject(bbox)
        m.add_form("F1", form)
        m.clear()
        assert m.count() == 0


# ── F68: ExtGState ───────────────────────────────────────────────────────────


class TestRenderingIntent:
    def test_variants(self):
        assert ox.RenderingIntent.ABSOLUTE_COLORIMETRIC is not None
        assert ox.RenderingIntent.RELATIVE_COLORIMETRIC is not None
        assert ox.RenderingIntent.SATURATION is not None
        assert ox.RenderingIntent.PERCEPTUAL is not None

    def test_repr(self):
        assert "PERCEPTUAL" in repr(ox.RenderingIntent.PERCEPTUAL)


class TestExtGState:
    def test_new_empty(self):
        s = ox.ExtGState()
        assert s.is_empty()
        assert not s.uses_transparency()

    def test_with_line_width(self):
        s = ox.ExtGState().with_line_width(2.5)
        assert not s.is_empty()

    def test_with_alpha(self):
        s = ox.ExtGState().with_alpha(0.5)
        assert s.uses_transparency()

    def test_with_alpha_stroke_fill(self):
        s = ox.ExtGState().with_alpha_stroke(0.8).with_alpha_fill(0.6)
        assert s.uses_transparency()

    def test_with_blend_mode(self):
        s = ox.ExtGState().with_blend_mode(ox.BlendMode.MULTIPLY)
        assert s.uses_transparency()

    def test_with_rendering_intent(self):
        s = ox.ExtGState().with_rendering_intent(ox.RenderingIntent.PERCEPTUAL)
        assert not s.is_empty()

    def test_with_line_cap_join(self):
        s = ox.ExtGState().with_line_cap(ox.LineCap.ROUND).with_line_join(ox.LineJoin.BEVEL)
        assert not s.is_empty()

    def test_with_miter_limit(self):
        s = ox.ExtGState().with_miter_limit(10.0)
        assert not s.is_empty()

    def test_with_overprint(self):
        s = ox.ExtGState().with_overprint_stroke(True).with_overprint_fill(False)
        assert not s.is_empty()

    def test_with_flatness_smoothness(self):
        s = ox.ExtGState().with_flatness(1.5).with_smoothness(0.5)
        assert not s.is_empty()

    def test_with_text_knockout(self):
        s = ox.ExtGState().with_text_knockout(False)
        assert not s.is_empty()

    def test_repr(self):
        s = ox.ExtGState()
        assert "ExtGState" in repr(s)


class TestExtGStateManager:
    def test_new_empty(self):
        m = ox.ExtGStateManager()
        assert m.count() == 0

    def test_add_state(self):
        m = ox.ExtGStateManager()
        state = ox.ExtGState().with_line_width(2.0)
        name = m.add_state(state)
        assert isinstance(name, str)
        assert m.count() == 1

    def test_add_empty_state_raises(self):
        m = ox.ExtGStateManager()
        state = ox.ExtGState()  # empty
        with pytest.raises(Exception):
            m.add_state(state)

    def test_clear(self):
        m = ox.ExtGStateManager()
        m.add_state(ox.ExtGState().with_line_width(1.0))
        m.clear()
        assert m.count() == 0


# ── F69: SoftMask + TransparencyGroup ────────────────────────────────────────


class TestSoftMaskType:
    def test_variants(self):
        assert ox.SoftMaskType.ALPHA is not None
        assert ox.SoftMaskType.LUMINOSITY is not None

    def test_repr(self):
        assert "ALPHA" in repr(ox.SoftMaskType.ALPHA)
        assert "LUMINOSITY" in repr(ox.SoftMaskType.LUMINOSITY)


class TestSoftMask:
    def test_none(self):
        m = ox.SoftMask.none()
        assert m.is_none()

    def test_alpha(self):
        m = ox.SoftMask.alpha("Group1")
        assert not m.is_none()

    def test_luminosity(self):
        m = ox.SoftMask.luminosity("Group2")
        assert not m.is_none()

    def test_with_background_color(self):
        m = ox.SoftMask.alpha("G1").with_background_color([1.0, 1.0, 1.0])
        assert not m.is_none()

    def test_with_bbox(self):
        m = ox.SoftMask.alpha("G1").with_bbox([0.0, 0.0, 100.0, 100.0])
        assert not m.is_none()

    def test_repr(self):
        m = ox.SoftMask.none()
        assert "none" in repr(m).lower()


class TestSoftMaskState:
    def test_new(self):
        s = ox.SoftMaskState()
        assert not s.is_active()

    def test_set_mask(self):
        s = ox.SoftMaskState()
        s.set_mask(ox.SoftMask.alpha("G1"))
        assert s.is_active()

    def test_push_pop(self):
        s = ox.SoftMaskState()
        s.set_mask(ox.SoftMask.alpha("G1"))
        s.push_mask(ox.SoftMask.luminosity("G2"))
        assert s.is_active()
        popped = s.pop_mask()
        assert popped is not None
        assert s.is_active()  # G1 is restored

    def test_clear(self):
        s = ox.SoftMaskState()
        s.set_mask(ox.SoftMask.alpha("G1"))
        s.clear()
        assert not s.is_active()


class TestTransparencyGroup:
    def test_new(self):
        g = ox.TransparencyGroup()
        assert g is not None

    def test_isolated_factory(self):
        g = ox.TransparencyGroup.isolated()
        assert g is not None

    def test_knockout_factory(self):
        g = ox.TransparencyGroup.knockout()
        assert g is not None

    def test_with_isolated(self):
        g = ox.TransparencyGroup().with_isolated(True)
        assert g is not None

    def test_with_knockout(self):
        g = ox.TransparencyGroup().with_knockout(True)
        assert g is not None

    def test_with_blend_mode(self):
        g = ox.TransparencyGroup().with_blend_mode(ox.BlendMode.MULTIPLY)
        assert g is not None

    def test_with_opacity(self):
        g = ox.TransparencyGroup().with_opacity(0.5)
        assert g is not None

    def test_with_color_space(self):
        g = ox.TransparencyGroup().with_color_space("DeviceCMYK")
        assert g is not None


# ── F70: Advanced Color Spaces ────────────────────────────────────────────────


class TestIccColorSpace:
    def test_variants(self):
        assert ox.IccColorSpace.RGB is not None
        assert ox.IccColorSpace.CMYK is not None
        assert ox.IccColorSpace.LAB is not None
        assert ox.IccColorSpace.GRAY is not None

    def test_repr(self):
        assert "RGB" in repr(ox.IccColorSpace.RGB)
        assert "CMYK" in repr(ox.IccColorSpace.CMYK)


class TestStandardIccProfile:
    def test_all_variants(self):
        variants = [
            ox.StandardIccProfile.S_RGB,
            ox.StandardIccProfile.ADOBE_RGB,
            ox.StandardIccProfile.PRO_PHOTO_RGB,
            ox.StandardIccProfile.USWC_SWOP_V2,
            ox.StandardIccProfile.COATED_FOGRA39,
            ox.StandardIccProfile.UNCOATED_FOGRA29,
            ox.StandardIccProfile.GRAY_GAMMA22,
        ]
        for v in variants:
            assert v is not None

    def test_repr(self):
        assert "S_RGB" in repr(ox.StandardIccProfile.S_RGB)
        assert "GRAY_GAMMA22" in repr(ox.StandardIccProfile.GRAY_GAMMA22)


class TestIccProfile:
    def test_from_standard_srgb(self):
        p = ox.IccProfile.from_standard(ox.StandardIccProfile.S_RGB)
        assert p.is_rgb()
        assert not p.is_cmyk()
        assert not p.is_gray()
        assert p.size() >= 128

    def test_from_standard_cmyk(self):
        p = ox.IccProfile.from_standard(ox.StandardIccProfile.COATED_FOGRA39)
        assert p.is_cmyk()
        assert not p.is_rgb()

    def test_from_standard_gray(self):
        p = ox.IccProfile.from_standard(ox.StandardIccProfile.GRAY_GAMMA22)
        assert p.is_gray()

    def test_all_standard_profiles_work(self):
        variants = [
            ox.StandardIccProfile.S_RGB,
            ox.StandardIccProfile.ADOBE_RGB,
            ox.StandardIccProfile.PRO_PHOTO_RGB,
            ox.StandardIccProfile.USWC_SWOP_V2,
            ox.StandardIccProfile.COATED_FOGRA39,
            ox.StandardIccProfile.UNCOATED_FOGRA29,
            ox.StandardIccProfile.GRAY_GAMMA22,
        ]
        for v in variants:
            p = ox.IccProfile.from_standard(v)
            assert p.size() >= 128

    def test_constructor(self):
        data = bytes([0] * 200)
        p = ox.IccProfile("TestProf", list(data), ox.IccColorSpace.RGB)
        assert p.name == "TestProf"
        assert p.is_rgb()

    def test_validate(self):
        p = ox.IccProfile.from_standard(ox.StandardIccProfile.S_RGB)
        p.validate()  # Should not raise

    def test_with_range(self):
        p = ox.IccProfile.from_standard(ox.StandardIccProfile.GRAY_GAMMA22)
        p2 = p.with_range([0.0, 1.0])
        assert p2 is not None

    def test_repr(self):
        p = ox.IccProfile.from_standard(ox.StandardIccProfile.S_RGB)
        assert "IccProfile" in repr(p)


class TestIccProfileManager:
    def test_new_empty(self):
        m = ox.IccProfileManager()
        assert m.count() == 0

    def test_create_default_srgb(self):
        m = ox.IccProfileManager()
        name = m.create_default_srgb()
        assert isinstance(name, str)
        assert m.count() == 1

    def test_create_default_cmyk(self):
        m = ox.IccProfileManager()
        name = m.create_default_cmyk()
        assert isinstance(name, str)
        assert m.count() == 1

    def test_create_default_gray(self):
        m = ox.IccProfileManager()
        name = m.create_default_gray()
        assert isinstance(name, str)
        assert m.count() == 1

    def test_add_standard_profile(self):
        m = ox.IccProfileManager()
        name = m.add_standard_profile(ox.StandardIccProfile.ADOBE_RGB)
        assert isinstance(name, str)
        assert m.count() == 1

    def test_add_profile(self):
        m = ox.IccProfileManager()
        p = ox.IccProfile.from_standard(ox.StandardIccProfile.S_RGB)
        name = m.add_profile(p)
        assert isinstance(name, str)
        assert m.count() == 1

    def test_clear(self):
        m = ox.IccProfileManager()
        m.create_default_srgb()
        m.clear()
        assert m.count() == 0


class TestSeparationColorSpace:
    def test_rgb_separation(self):
        cs = ox.SeparationColorSpace.rgb_separation("Red", 1.0, 0.0, 0.0)
        assert cs.colorant_name == "Red"

    def test_cmyk_separation(self):
        cs = ox.SeparationColorSpace.cmyk_separation("Cyan", 1.0, 0.0, 0.0, 0.0)
        assert cs.colorant_name == "Cyan"

    def test_apply_tint(self):
        cs = ox.SeparationColorSpace.rgb_separation("Blue", 0.0, 0.0, 1.0)
        values = cs.apply_tint(1.0)
        # At full tint: white→blue transition, so blue channel at max
        assert values[2] == 1.0

    def test_repr(self):
        cs = ox.SeparationColorSpace.rgb_separation("Gold", 1.0, 0.8, 0.0)
        assert "SeparationColorSpace" in repr(cs)


class TestSeparationColor:
    def test_constructor(self):
        cs = ox.SeparationColorSpace.rgb_separation("Red", 1.0, 0.0, 0.0)
        c = ox.SeparationColor(cs, 0.75)
        assert c.tint == 0.75
        assert c.colorant_name() == "Red"

    def test_to_rgb(self):
        cs = ox.SeparationColorSpace.rgb_separation("Blue", 0.0, 0.0, 1.0)
        c = ox.SeparationColor(cs, 1.0)
        rgb = c.to_rgb()
        assert isinstance(rgb, ox.Color)

    def test_tint_clamping(self):
        cs = ox.SeparationColorSpace.rgb_separation("Test", 1.0, 0.0, 0.0)
        c = ox.SeparationColor(cs, 1.5)
        assert c.tint == 1.0


class TestSpotColors:
    def test_pantone_185c(self):
        cs = ox.SpotColors.pantone_185c()
        assert cs.colorant_name == "PANTONE 185 C"

    def test_pantone_286c(self):
        cs = ox.SpotColors.pantone_286c()
        assert cs.colorant_name == "PANTONE 286 C"

    def test_pantone_376c(self):
        cs = ox.SpotColors.pantone_376c()
        assert cs.colorant_name == "PANTONE 376 C"

    def test_gold(self):
        cs = ox.SpotColors.gold()
        assert cs.colorant_name == "Gold"

    def test_silver(self):
        cs = ox.SpotColors.silver()
        assert cs.colorant_name == "Silver"

    def test_varnish(self):
        cs = ox.SpotColors.varnish()
        assert cs.colorant_name == "Varnish"
