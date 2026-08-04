import unittest
from fractions import Fraction

from wanresolutions import (
    LTX_UPSCALER_POWER_CHOICES,
    LTXResolutions,
    LTXUpscalerPower,
    MiniMaxH3Resolutions,
    WanResolutions,
)


class LTXUpscalerPowerTests(unittest.TestCase):
    def setUp(self):
        self.node = LTXResolutions()

    def test_ltx_input_types_include_upscaler_power_combo_without_override(self):
        inputs = LTXResolutions.INPUT_TYPES()

        self.assertEqual(inputs["required"]["upscaler_power"][0], "COMBO")
        self.assertEqual(
            inputs["required"]["upscaler_power"][1]["options"],
            list(LTX_UPSCALER_POWER_CHOICES),
        )
        self.assertNotIn("upscaler_power_override", inputs["optional"])

    def test_none_preserves_selected_target(self):
        self.assertEqual(
            self.node.pick(
                "16:9",
                "Full HD Output — 1920×1088",
                upscaler_power="none",
            ),
            (1920, 1088),
        )

    def test_full_hd_label_is_not_mistaken_for_hd_output(self):
        self.assertEqual(
            LTXResolutions._parse_resolution(
                "16:9",
                "Full HD Output — 1920×1088",
            ),
            (1920, 1088),
        )

    def test_x2_outputs_official_landscape_base_pair(self):
        self.assertEqual(
            self.node.pick(
                "16:9",
                "Full HD Output — 1920×1088",
                upscaler_power="x2",
            ),
            (960, 544),
        )

    def test_x1_5_rounds_target_up_to_a_compatible_grid(self):
        self.assertEqual(
            self.node.pick(
                "16:9",
                "Full HD Output — 1920×1088",
                upscaler_power="x1.5",
            ),
            (1280, 768),
        )

    def test_connected_combo_value_is_used_directly(self):
        self.assertEqual(
            self.node.pick(
                "16:9",
                "Full HD Output — 1920×1088",
                upscaler_power="2x",
            ),
            (960, 544),
        )

    def test_all_scaled_outputs_are_legal_base_resolutions(self):
        factors = {"x1.5": Fraction(3, 2), "x2": Fraction(2, 1)}

        for aspect_ratio, rows in LTXResolutions.PRESETS.items():
            for width, height, note in rows:
                label = f"{note} — {width}×{height}"
                for power, factor in factors.items():
                    with self.subTest(aspect_ratio=aspect_ratio, label=label, power=power):
                        base_width, base_height = self.node.pick(
                            aspect_ratio,
                            label,
                            upscaler_power=power,
                        )
                        self.assertEqual(base_width % 32, 0)
                        self.assertEqual(base_height % 32, 0)
                        self.assertEqual((base_width * factor.numerator) % factor.denominator, 0)
                        self.assertEqual((base_height * factor.numerator) % factor.denominator, 0)

    def test_support_node_outputs_normalized_combo(self):
        self.assertEqual(LTXUpscalerPower.RETURN_TYPES, ("COMBO",))
        self.assertEqual(LTXUpscalerPower().select("1.5x"), ("x1.5",))

    def test_wan_native_16_9_is_official_720p(self):
        self.assertEqual(
            WanResolutions().pick("16:9", "Wan 2.2 Native — 1280×720"),
            (1280, 720),
        )

    def test_wan_presets_are_div16(self):
        for rows in WanResolutions.PRESETS.values():
            for w, h, _note in rows:
                self.assertEqual((w % 16, h % 16), (0, 0), msg=f"{w}x{h}")

    def test_wan_no_round_to_16_flag(self):
        self.assertNotIn("round_to_16", WanResolutions.INPUT_TYPES()["required"])
        self.assertIn("official_only", WanResolutions.INPUT_TYPES()["required"])

    def test_official_only_snaps_to_buckets(self):
        node = WanResolutions()
        # 16:9 High Detail (1104x624) -> nearest landscape official by area = 720p
        self.assertEqual(
            node.pick("16:9", "High Detail — 1104×624", official_only=True),
            (1280, 720),
        )
        # 9:16 Preview (480x848) -> nearest portrait official by area = 480p
        self.assertEqual(
            node.pick("9:16", "Preview — 480×848", official_only=True),
            (480, 832),
        )
        # square -> treated as landscape
        self.assertEqual(
            node.pick("1:1", "Wan 2.2 Native — 960×960", official_only=True),
            (1280, 720),
        )

    def test_official_labels_are_orientation_filtered(self):
        self.assertEqual(
            WanResolutions._official_labels_for("16:9"),
            ["Official 480P — 832×480", "Official 720P — 1280×720"],
        )
        self.assertEqual(
            WanResolutions._official_labels_for("9:16"),
            ["Official 480P — 480×832", "Official 720P — 720×1280"],
        )

    def test_official_labels_are_accepted_by_validation(self):
        # The frontend swaps these into the dropdown. Custom validation accepts
        # them without requiring the backend combo to expose a full union.
        for label in (
            "Official 480P — 832×480",
            "Official 720P — 1280×720",
            "Official 480P — 480×832",
            "Official 720P — 720×1280",
        ):
            self.assertTrue(WanResolutions.VALIDATE_INPUTS(resolution=label))

    def test_backend_combo_is_seeded_with_only_the_default_aspect(self):
        choices = WanResolutions.INPUT_TYPES()["required"]["resolution"][0]
        self.assertEqual(choices, WanResolutions._labels_for("1:1"))
        self.assertNotIn("Wan 2.2 Native — 1280×720", choices)

    def test_official_label_round_trips(self):
        node = WanResolutions()
        self.assertEqual(
            node.pick("16:9", "Official 720P — 1280×720", official_only=True),
            (1280, 720),
        )
        self.assertEqual(
            node.pick("9:16", "Official 480P — 480×832", official_only=True),
            (480, 832),
        )

    def test_validate_inputs_accepts_legacy_or_unknown_labels(self):
        # Old preset labels are no longer in the seeded combo; VALIDATE_INPUTS must
        # let them through so headless/API replays of old workflows still run.
        choices = set(WanResolutions.INPUT_TYPES()["required"]["resolution"][0])
        self.assertNotIn("Fast Samples — 480×480", choices)
        self.assertTrue(WanResolutions.VALIDATE_INPUTS(resolution="Fast Samples — 480×480"))
        self.assertTrue(WanResolutions.VALIDATE_INPUTS(resolution="literally anything"))

    def test_legacy_label_still_produces_valid_output(self):
        # Whatever reaches pick() must yield a usable div-16 size, never an error.
        for ar, label in [
            ("1:1", "Fast Samples — 480×480"),
            ("16:9", "Wan 2.2 Native — 1264×720"),
            ("2:3", "Reasonable — 624×912"),
        ]:
            w, h = WanResolutions().pick(ar, label)
            self.assertEqual((w % 16, h % 16), (0, 0), msg=f"{ar} {label} -> {w}x{h}")


class MiniMaxH3ResolutionTests(unittest.TestCase):
    class Image:
        shape = (1, 641, 1000, 3)

    def test_t2v_uses_official_h3_aspect_ratios(self):
        self.assertEqual(
            MiniMaxH3Resolutions.ASPECT_ORDER,
            ("1:1", "3:4", "4:3", "9:16", "16:9", "21:9"),
        )
        self.assertEqual(
            MiniMaxH3Resolutions.INPUT_TYPES()["required"]["aspect_ratio"][1]["default"],
            "16:9",
        )

    def test_backend_combo_does_not_expose_the_full_resolution_union(self):
        choices = MiniMaxH3Resolutions.INPUT_TYPES()["required"]["resolution"][0]
        self.assertEqual(choices, MiniMaxH3Resolutions._labels_for("16:9"))
        self.assertEqual(len(choices), 6)
        self.assertNotIn("2K (2.25 MP) — 1536×1536", choices)

    def test_each_t2v_aspect_has_six_div32_buckets(self):
        for aspect_ratio, rows in MiniMaxH3Resolutions.PRESETS.items():
            self.assertEqual(len(rows), 6, msg=aspect_ratio)
            for width, height, _note in rows:
                self.assertEqual(
                    (width % 32, height % 32),
                    (0, 0),
                    msg=f"{aspect_ratio}: {width}x{height}",
                )

    def test_landscape_1k_and_2k_anchors(self):
        node = MiniMaxH3Resolutions()
        self.assertEqual(node.pick("16:9", "1K (0.56 MP) — 1024×576"), (1024, 576))
        self.assertEqual(node.pick("16:9", "2K (2.25 MP) — 2048×1152"), (2048, 1152))

    def test_i2v_preserves_source_ratio_with_smart_area_sizing(self):
        output = MiniMaxH3Resolutions().pick(
            "1:1",
            "2K (2.25 MP) — 1536×1536",
            image=self.Image(),
        )

        self.assertEqual(output["result"], (1920, 1216))
        self.assertEqual(output["result"][0] % 32, 0)
        self.assertEqual(output["result"][1] % 32, 0)
        source_ratio = 1000 / 641
        output_ratio = output["result"][0] / output["result"][1]
        self.assertLess(abs(output_ratio - source_ratio), 0.02)

    def test_i2v_reports_nearest_official_aspect_without_snapping_output_to_it(self):
        output = MiniMaxH3Resolutions().pick(
            "1:1",
            "Preview (0.40 MP) — 640×640",
            image=self.Image(),
        )

        state = output["ui"]["aspect_resolution_state"][0]
        self.assertEqual(state["aspect_ratio"], "16:9")
        self.assertEqual((state["source_width"], state["source_height"]), (1000, 641))
        self.assertEqual(output["result"], (800, 512))


if __name__ == "__main__":
    unittest.main()
