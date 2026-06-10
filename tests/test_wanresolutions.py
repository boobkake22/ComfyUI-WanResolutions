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

    def test_wan_node_behavior_is_unchanged(self):
        self.assertEqual(
            WanResolutions().pick("1:1", "Fast Samples — 480×480"),
            (480, 480),
        )


if __name__ == "__main__":
    unittest.main()
