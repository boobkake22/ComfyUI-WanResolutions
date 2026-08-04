import math
import re
from fractions import Fraction
from typing import Dict, List, Optional, Tuple


LTX_UPSCALER_POWER_CHOICES = ("none", "x1.5", "x2")
LTX_UPSCALER_POWER_FACTORS = {
    "none": Fraction(1, 1),
    "x1.5": Fraction(3, 2),
    "x2": Fraction(2, 1),
}


class AspectResolutionNodeBase:
    """
    Shared aspect-ratio resolution picker for video models.
    - Choose aspect ratio and quality tier.
    - Optional IMAGE input can auto-select the closest supported aspect ratio.
    - Outputs width,height as INT.
    """

    FUNCTION = "pick"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    UI_STATE_KEYS = ("aspect_resolution_state", "wanresolutions_state")

    FALLBACK_ASPECT = "1:1"
    ASPECT_ORDER = ("1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9")
    ALLOW_OFFICIAL_ONLY = False
    ALLOW_IMAGE_BYPASS = False
    ALLOW_UPSCALER_POWER = False
    LEGACY_NOTE_ALIASES: Dict[str, str] = {}
    OFFICIAL_SIZES: List[Tuple[int, int]] = []
    PRESETS: Dict[str, List[Tuple[int, int, str]]] = {}

    @classmethod
    def _rows_for(cls, aspect_ratio: str) -> List[Tuple[int, int, str]]:
        return cls.PRESETS.get(aspect_ratio) or cls.PRESETS[cls.FALLBACK_ASPECT]

    @classmethod
    def _labels_for(cls, aspect_ratio: str) -> List[str]:
        rows = cls._rows_for(aspect_ratio)
        return [f"{note} — {w}×{h}" for w, h, note in rows]

    @classmethod
    def _legacy_note(cls, note: str) -> str:
        return cls.LEGACY_NOTE_ALIASES.get(note, note.lower())

    @classmethod
    def _legacy_labels_for(cls, aspect_ratio: str) -> List[str]:
        rows = cls._rows_for(aspect_ratio)
        out = []
        for i, (w, h, note) in enumerate(rows, start=1):
            out.append(f"{i}. {w}×{h} — {cls._legacy_note(note)}")
        return out

    @staticmethod
    def _normalize_text(value: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"[\(\)]", "", value or "").lower()).strip()

    @staticmethod
    def _parse_size(value: str) -> Optional[Tuple[int, int]]:
        m = re.search(r"(\d+)\s*[x×]\s*(\d+)", value or "", flags=re.IGNORECASE)
        if not m:
            return None
        return int(m.group(1)), int(m.group(2))

    @classmethod
    def INPUT_TYPES(cls):
        aspect_choices = list(cls.ASPECT_ORDER)
        default_ar = cls.FALLBACK_ASPECT
        # Seed the combo with only the default aspect's resolutions. The frontend
        # swaps this list when the aspect changes, while VALIDATE_INPUTS accepts
        # saved/API labels from every aspect. Returning the full union here causes
        # an unfiltered list to flash—or remain visible if custom JS loads late.
        resolution_choices = cls._labels_for(default_ar)
        default_res = cls._labels_for(default_ar)[0]

        required = {
            "aspect_ratio": (aspect_choices, {"default": default_ar}),
            "resolution": (resolution_choices, {"default": default_res}),
        }
        if cls.ALLOW_OFFICIAL_ONLY:
            required["official_only"] = ("BOOLEAN", {"default": False})
        if cls.ALLOW_IMAGE_BYPASS:
            required["image_bypass"] = ("BOOLEAN", {"default": False})
        if cls.ALLOW_UPSCALER_POWER:
            required["upscaler_power"] = (
                "COMBO",
                {
                    "options": list(LTX_UPSCALER_POWER_CHOICES),
                    "default": "none",
                },
            )

        return {
            "required": required,
            "optional": {
                "image": ("IMAGE",),
            },
        }

    @classmethod
    def VALIDATE_INPUTS(cls, resolution=None):
        # `resolution` is parsed leniently in pick(), so a workflow saved against an
        # older preset table (whose label is no longer in the current combo list)
        # still loads and runs instead of being rejected by ComfyUI's strict combo
        # validation. Declaring `resolution` here tells ComfyUI to skip the default
        # list-membership check for it and defer to this method, which always accepts.
        return True

    @classmethod
    def _parse_index(cls, label: str) -> Optional[int]:
        m = re.match(r"\s*(\d+)\s*[\.\)]", label or "")
        if not m:
            return None
        return int(m.group(1)) - 1

    @classmethod
    def _tier_index_for_value(cls, aspect_ratio: str, resolution_label: str) -> Optional[int]:
        rows = cls._rows_for(aspect_ratio)
        normalized_value = cls._normalize_text(resolution_label)

        note_matches = sorted(
            enumerate(rows),
            key=lambda indexed_row: len(cls._normalize_text(indexed_row[1][2])),
            reverse=True,
        )
        for i, (_, _, note) in note_matches:
            if cls._normalize_text(note) in normalized_value:
                return i

        idx = cls._parse_index(resolution_label)
        if idx is not None:
            return max(0, min(idx, len(rows) - 1))

        parsed_size = cls._parse_size(resolution_label)
        if parsed_size is not None:
            width, height = parsed_size
            for i, (row_w, row_h, _) in enumerate(rows):
                if row_w == width and row_h == height:
                    return i

        return None

    @classmethod
    def _label_for_dimensions(cls, aspect_ratio: str, width: int, height: int) -> Optional[str]:
        for row_w, row_h, note in cls._rows_for(aspect_ratio):
            if row_w == width and row_h == height:
                return f"{note} — {row_w}×{row_h}"
        return None

    @staticmethod
    def _official_label(width: int, height: int) -> str:
        return f"Official {min(int(width), int(height))}P — {int(width)}×{int(height)}"

    @classmethod
    def _official_sizes_for_orientation(cls, landscape: bool) -> List[Tuple[int, int]]:
        pool = [s for s in cls.OFFICIAL_SIZES if (s[0] >= s[1]) == landscape]
        pool = pool or list(cls.OFFICIAL_SIZES)
        return sorted(pool, key=lambda wh: wh[0] * wh[1])

    @classmethod
    def _official_labels_for(cls, aspect_ratio: str) -> List[str]:
        if not cls.OFFICIAL_SIZES:
            return []
        ratio = cls._parse_aspect_ratio_value(aspect_ratio)
        landscape = True if ratio is None else ratio >= 1.0
        return [cls._official_label(w, h) for w, h in cls._official_sizes_for_orientation(landscape)]

    @classmethod
    def _snap_official(
        cls, width: int, height: int, aspect_ratio: Optional[str] = None
    ) -> Tuple[int, int]:
        """Snap to the nearest official bucket. Orientation follows the resolved aspect
        ratio when given (so an attached image can drive it), otherwise width/height.
        The 480p vs 720p choice is the nearest official by area (square→landscape)."""
        if not cls.OFFICIAL_SIZES:
            return int(width), int(height)
        ratio = cls._parse_aspect_ratio_value(aspect_ratio) if aspect_ratio else None
        landscape = (width >= height) if ratio is None else ratio >= 1.0
        pool = cls._official_sizes_for_orientation(landscape)
        area = int(width) * int(height)
        best = min(pool, key=lambda wh: (abs(wh[0] * wh[1] - area), wh))
        return int(best[0]), int(best[1])

    @classmethod
    def _parse_resolution(cls, aspect_ratio: str, resolution_label: str) -> Tuple[int, int]:
        """
        Robust parsing for new and old workflows:
        1) Prefer matching note text (keeps same tier across aspect changes).
        2) Fallback: parse leading index "N." and map by aspect ratio.
        3) Fallback: extract WxH.
        """
        rows = cls._rows_for(aspect_ratio)
        idx = cls._tier_index_for_value(aspect_ratio, resolution_label)
        if idx is not None:
            w, h, _ = rows[idx]
            return w, h

        parsed_size = cls._parse_size(resolution_label)
        if parsed_size is not None:
            return parsed_size

        w, h, _ = rows[0]
        return w, h

    @staticmethod
    def _round_up_to_multiple(value: int, multiple: int) -> int:
        if multiple <= 0:
            return int(value)
        return max(multiple, ((int(value) + multiple - 1) // multiple) * multiple)

    @staticmethod
    def _normalize_upscaler_power(value: Optional[str]) -> str:
        normalized = re.sub(r"\s+", "", str(value or "none").lower())
        aliases = {
            "1": "none",
            "1.0": "none",
            "x1": "none",
            "x1.0": "none",
            "1x": "none",
            "1.0x": "none",
            "1.5": "x1.5",
            "1.5x": "x1.5",
            "2": "x2",
            "2.0": "x2",
            "2x": "x2",
            "x2.0": "x2",
        }
        normalized = aliases.get(normalized, normalized)
        return normalized if normalized in LTX_UPSCALER_POWER_FACTORS else "none"

    @classmethod
    def _apply_upscaler_power(
        cls,
        width: int,
        height: int,
        upscaler_power: Optional[str],
    ) -> Tuple[int, int]:
        factor = LTX_UPSCALER_POWER_FACTORS[cls._normalize_upscaler_power(upscaler_power)]
        if factor == 1:
            return int(width), int(height)

        # Base dimensions must be divisible by 32. This makes the compatible
        # final-resolution step 32 * the reduced fraction numerator.
        final_step = 32 * factor.numerator
        final_width = cls._round_up_to_multiple(width, final_step)
        final_height = cls._round_up_to_multiple(height, final_step)
        return (
            final_width * factor.denominator // factor.numerator,
            final_height * factor.denominator // factor.numerator,
        )

    @staticmethod
    def _parse_aspect_ratio_value(aspect_ratio: str) -> Optional[float]:
        m = re.match(r"^\s*(\d+)\s*:\s*(\d+)\s*$", aspect_ratio or "")
        if not m:
            return None
        w = max(1, int(m.group(1)))
        h = max(1, int(m.group(2)))
        return float(w) / float(h)

    @classmethod
    def _best_aspect_ratio(cls, width: int, height: int) -> str:
        if width <= 0 or height <= 0:
            return cls.FALLBACK_ASPECT

        target = float(width) / float(height)
        best_ar = cls.FALLBACK_ASPECT
        best_delta = float("inf")

        for ar in cls.ASPECT_ORDER:
            ratio = cls._parse_aspect_ratio_value(ar)
            if ratio is None:
                continue
            delta = abs(ratio - target)
            if delta < best_delta:
                best_delta = delta
                best_ar = ar

        return best_ar

    @staticmethod
    def _image_dimensions(image) -> Optional[Tuple[int, int]]:
        if image is None:
            return None

        if isinstance(image, (list, tuple)):
            if not image:
                return None
            image = image[0]

        shape = getattr(image, "shape", None)
        if shape is None:
            return None

        dims = tuple(int(v) for v in shape)
        if len(dims) == 4:
            _, h, w, _ = dims
            return (w, h)
        if len(dims) == 3:
            if dims[-1] in (1, 3, 4):
                h, w, _ = dims
                return (w, h)
            if dims[0] in (1, 3, 4):
                _, h, w = dims
                return (w, h)
            h, w, _ = dims
            return (w, h)
        if len(dims) == 2:
            h, w = dims
            return (w, h)

        return None

    def pick(
        self,
        aspect_ratio: str,
        resolution: str,
        image=None,
        official_only: bool = False,
        image_bypass: bool = False,
        upscaler_power: str = "none",
    ):
        resolved_aspect = aspect_ratio
        image_input = None if (self.ALLOW_IMAGE_BYPASS and image_bypass) else image
        image_dims = self._image_dimensions(image_input)
        image_w = None
        image_h = None
        if image_dims is not None:
            image_w, image_h = image_dims
            resolved_aspect = self._best_aspect_ratio(image_w, image_h)

        w, h = self._parse_resolution(resolved_aspect, resolution)
        if self.ALLOW_OFFICIAL_ONLY and official_only:
            w, h = self._snap_official(w, h, aspect_ratio=resolved_aspect)
            resolved_resolution = self._official_label(w, h)
        else:
            resolved_resolution = self._label_for_dimensions(resolved_aspect, w, h) or resolution
        if self.ALLOW_UPSCALER_POWER:
            w, h = self._apply_upscaler_power(w, h, upscaler_power)

        result = (int(w), int(h))
        if image_dims is None:
            return result

        state = {
            "aspect_ratio": resolved_aspect,
            "resolution": resolved_resolution,
            "source_width": image_w,
            "source_height": image_h,
        }
        return {
            "ui": {key: [state] for key in self.UI_STATE_KEYS},
            "result": result,
        }


class WanResolutions(AspectResolutionNodeBase):
    """
    Wan 2.2 (A14B) resolution presets. Every size is divisible by 16 — the real
    alignment requirement for the A14B T2V/I2V models (8x VAE stride x 2x DiT
    patch). The lower tiers are faster, lower-area conveniences; "Wan 2.2 Native"
    matches what the model actually targets. Enable `official_only` to snap output
    to one of Wan's four CLI buckets (1280x720 / 720x1280 / 832x480 / 480x832).
    """

    CATEGORY = "WAN"
    ALLOW_OFFICIAL_ONLY = True
    OFFICIAL_SIZES = [(1280, 720), (720, 1280), (832, 480), (480, 832)]
    LEGACY_NOTE_ALIASES = {"Wan 2.2 Native": "(WAN 2.2 native)"}

    PRESETS: Dict[str, List[Tuple[int, int, str]]] = {
        "1:1": [
            (480, 480, "Fast Draft"),
            (640, 640, "Preview"),
            (832, 832, "High Detail"),
            (960, 960, "Wan 2.2 Native"),
        ],
        "2:3": [
            (384, 576, "Fast Draft"),
            (512, 768, "Preview"),
            (672, 1008, "High Detail"),
            (768, 1168, "Wan 2.2 Native"),
        ],
        "3:2": [
            (576, 384, "Fast Draft"),
            (768, 512, "Preview"),
            (1008, 672, "High Detail"),
            (1168, 768, "Wan 2.2 Native"),
        ],
        "3:4": [
            (432, 576, "Fast Draft"),
            (576, 768, "Preview"),
            (720, 960, "High Detail"),
            (816, 1104, "Wan 2.2 Native"),
        ],
        "4:3": [
            (576, 432, "Fast Draft"),
            (768, 576, "Preview"),
            (960, 720, "High Detail"),
            (1104, 816, "Wan 2.2 Native"),
        ],
        "9:16": [
            (352, 624, "Fast Draft"),
            (480, 848, "Preview"),
            (624, 1104, "High Detail"),
            (720, 1280, "Wan 2.2 Native"),
        ],
        "16:9": [
            (624, 352, "Fast Draft"),
            (848, 480, "Preview"),
            (1104, 624, "High Detail"),
            (1280, 720, "Wan 2.2 Native"),
        ],
    }


class MiniMaxH3Resolutions(AspectResolutionNodeBase):
    """
    MiniMax H3 resolution presets.

    Text-to-video uses MiniMax's six official aspect-ratio choices. Connecting
    an image switches to adaptive image-to-video sizing: the selected tier's
    pixel area is retained while the source image's aspect ratio is preserved.
    Every output is aligned to H3's 32-pixel transformer grid.
    """

    CATEGORY = "MINIMAX"
    FALLBACK_ASPECT = "16:9"
    ASPECT_ORDER = ("1:1", "3:4", "4:3", "9:16", "16:9", "21:9")

    # These areas give a useful local-generation ladder while retaining familiar
    # 1K / 1.5K / 2K landscape anchors. They are also used for adaptive I2V.
    TARGET_PIXELS = (
        512 * 512,
        int(0.40 * 1024 * 1024),
        1024 * 576,
        1344 * 768,
        1536 * 864,
        2048 * 1152,
    )

    PRESETS: Dict[str, List[Tuple[int, int, str]]] = {
        "1:1": [
            (512, 512, "Draft (0.25 MP)"),
            (640, 640, "Preview (0.40 MP)"),
            (768, 768, "1K (0.56 MP)"),
            (1024, 1024, "High Detail (1.00 MP)"),
            (1152, 1152, "1.5K (1.27 MP)"),
            (1536, 1536, "2K (2.25 MP)"),
        ],
        "3:4": [
            (448, 576, "Draft (0.25 MP)"),
            (576, 736, "Preview (0.40 MP)"),
            (672, 896, "1K (0.56 MP)"),
            (864, 1184, "High Detail (1.00 MP)"),
            (992, 1344, "1.5K (1.27 MP)"),
            (1344, 1760, "2K (2.25 MP)"),
        ],
        "4:3": [
            (576, 448, "Draft (0.25 MP)"),
            (736, 576, "Preview (0.40 MP)"),
            (896, 672, "1K (0.56 MP)"),
            (1184, 864, "High Detail (1.00 MP)"),
            (1344, 992, "1.5K (1.27 MP)"),
            (1760, 1344, "2K (2.25 MP)"),
        ],
        "9:16": [
            (384, 672, "Draft (0.25 MP)"),
            (480, 864, "Preview (0.40 MP)"),
            (576, 1024, "1K (0.56 MP)"),
            (768, 1344, "High Detail (1.00 MP)"),
            (864, 1536, "1.5K (1.27 MP)"),
            (1152, 2048, "2K (2.25 MP)"),
        ],
        "16:9": [
            (672, 384, "Draft (0.25 MP)"),
            (864, 480, "Preview (0.40 MP)"),
            (1024, 576, "1K (0.56 MP)"),
            (1344, 768, "High Detail (1.00 MP)"),
            (1536, 864, "1.5K (1.27 MP)"),
            (2048, 1152, "2K (2.25 MP)"),
        ],
        "21:9": [
            (768, 320, "Draft (0.25 MP)"),
            (992, 416, "Preview (0.40 MP)"),
            (1184, 512, "1K (0.56 MP)"),
            (1536, 672, "High Detail (1.00 MP)"),
            (1760, 768, "1.5K (1.27 MP)"),
            (2336, 992, "2K (2.25 MP)"),
        ],
    }

    @staticmethod
    def _adaptive_size(width: int, height: int, target_pixels: int) -> Tuple[int, int]:
        if width <= 0 or height <= 0:
            return (32, 32)

        ratio = float(width) / float(height)
        ideal_width = math.sqrt(float(target_pixels) * ratio)
        ideal_height = math.sqrt(float(target_pixels) / ratio)
        return (
            max(32, round(ideal_width / 32) * 32),
            max(32, round(ideal_height / 32) * 32),
        )

    def pick(
        self,
        aspect_ratio: str,
        resolution: str,
        image=None,
        official_only: bool = False,
        image_bypass: bool = False,
        upscaler_power: str = "none",
    ):
        image_dims = self._image_dimensions(image)
        if image_dims is None:
            return super().pick(
                aspect_ratio,
                resolution,
                image=None,
                official_only=official_only,
                image_bypass=image_bypass,
                upscaler_power=upscaler_power,
            )

        image_w, image_h = image_dims
        tier_index = self._tier_index_for_value(aspect_ratio, resolution)
        parsed_size = self._parse_size(resolution)
        if tier_index is None:
            target_pixels = (
                parsed_size[0] * parsed_size[1]
                if parsed_size is not None
                else self.TARGET_PIXELS[0]
            )
            tier_index = 0
        else:
            target_pixels = self.TARGET_PIXELS[tier_index]

        width, height = self._adaptive_size(image_w, image_h, target_pixels)
        resolved_aspect = self._best_aspect_ratio(image_w, image_h)
        resolved_resolution = self._labels_for(resolved_aspect)[tier_index]
        state = {
            "aspect_ratio": resolved_aspect,
            "resolution": resolved_resolution,
            "source_width": image_w,
            "source_height": image_h,
        }
        return {
            "ui": {key: [state] for key in self.UI_STATE_KEYS},
            "result": (int(width), int(height)),
        }


class LTXResolutions(AspectResolutionNodeBase):
    """
    LTX 2.3 video resolution presets.
    - Uses dimensions divisible by 32.
    - Keeps the same aspect-ratio selection workflow as WanResolutions.
    """

    CATEGORY = "LTX"
    ALLOW_IMAGE_BYPASS = True
    ALLOW_UPSCALER_POWER = True

    PRESETS: Dict[str, List[Tuple[int, int, str]]] = {
        "1:1": [
            (320, 320, "Stage 1 Preview"),
            (640, 640, "Fast Iteration"),
            (768, 768, "Balanced"),
            (960, 960, "HD Output"),
            (1184, 1184, "High Detail"),
            (1440, 1440, "Full HD Output"),
        ],
        "2:3": [
            (256, 384, "Stage 1 Preview"),
            (512, 768, "Fast Iteration"),
            (640, 960, "Balanced"),
            (768, 1152, "HD Output"),
            (960, 1440, "High Detail"),
            (1152, 1728, "Full HD Output"),
        ],
        "3:2": [
            (384, 256, "Stage 1 Preview"),
            (768, 512, "Fast Iteration"),
            (960, 640, "Balanced"),
            (1152, 768, "HD Output"),
            (1440, 960, "High Detail"),
            (1728, 1152, "Full HD Output"),
        ],
        "3:4": [
            (256, 352, "Stage 1 Preview"),
            (512, 704, "Fast Iteration"),
            (640, 864, "Balanced"),
            (864, 1152, "HD Output"),
            (1056, 1408, "High Detail"),
            (1248, 1664, "Full HD Output"),
        ],
        "4:3": [
            (352, 256, "Stage 1 Preview"),
            (704, 512, "Fast Iteration"),
            (864, 640, "Balanced"),
            (1152, 864, "HD Output"),
            (1408, 1056, "High Detail"),
            (1664, 1248, "Full HD Output"),
        ],
        "9:16": [
            (288, 512, "Stage 1 Preview"),
            (544, 960, "Fast Iteration"),
            (672, 1184, "Balanced"),
            (736, 1312, "HD Output"),
            (864, 1536, "High Detail"),
            (1088, 1920, "Full HD Output"),
        ],
        "16:9": [
            (512, 288, "Stage 1 Preview"),
            (960, 544, "Fast Iteration"),
            (1184, 672, "Balanced"),
            (1312, 736, "HD Output"),
            (1536, 864, "High Detail"),
            (1920, 1088, "Full HD Output"),
        ],
    }


class LTXUpscalerPower:
    """
    Connectable LTX upscaler-power value for the LTXResolutions combo.
    """

    CATEGORY = "LTX"
    FUNCTION = "select"
    RETURN_TYPES = ("COMBO",)
    RETURN_NAMES = ("upscaler_power",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "upscaler_power": (
                    "COMBO",
                    {
                        "options": list(LTX_UPSCALER_POWER_CHOICES),
                        "default": "none",
                    },
                ),
            },
        }

    def select(self, upscaler_power: str):
        return (AspectResolutionNodeBase._normalize_upscaler_power(upscaler_power),)
