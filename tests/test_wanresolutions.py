import unittest
from fractions import Fraction

from wanresolutions import (
    LTX_UPSCALER_POWER_CHOICES,
    LTXResolutions,
    LTXUpscalerPower,
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
        # The dropdown swaps to these labels, so the backend combo must accept them.
        valid = set(WanResolutions.INPUT_TYPES()["required"]["resolution"][0])
        for label in (
            "Official 480P — 832×480",
            "Official 720P — 1280×720",
            "Official 480P — 480×832",
            "Official 720P — 720×1280",
        ):
            self.assertIn(label, valid)

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
        # Old preset labels are no longer in the combo union; VALIDATE_INPUTS must
        # let them through so headless/API replays of old workflows still run.
        union = set(WanResolutions.INPUT_TYPES()["required"]["resolution"][0])
        self.assertNotIn("Fast Samples — 480×480", union)
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


if __name__ == "__main__":
    unittest.main()
