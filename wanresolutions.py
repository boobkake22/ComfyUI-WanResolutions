import re
from typing import Dict, List, Optional, Tuple


class WanResolutions:
    """
    WanResolutions
    - Choose aspect ratio and quality tier.
    - Optional IMAGE input can auto-select the closest aspect ratio.
    - Optional round_to_16 can snap output dimensions to multiples of 16.
    - Outputs width,height as INT.
    """

    CATEGORY = "WAN"
    FUNCTION = "pick"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    FALLBACK_ASPECT = "1:1"
    ASPECT_ORDER = ("1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9")

    # Presets: (width, height, note)
    PRESETS: Dict[str, List[Tuple[int, int, str]]] = {
        "1:1": [
            (480, 480, "Fast Samples"),
            (640, 640, "Fast and OK"),
            (768, 768, "Reasonable"),
            (800, 800, "Better Details"),
            (880, 880, "Really Good"),
            (960, 960, "Wan 2.2 Native"),
        ],
        "2:3": [
            (384, 576, "Fast Samples"),
            (528, 768, "Fast and OK"),
            (624, 912, "Reasonable"),
            (656, 960, "Better Details"),
            (736, 1072, "Really Good"),
            (784, 1136, "Wan 2.2 Native"),
        ],
        "3:2": [
            (576, 384, "Fast Samples"),
            (768, 528, "Fast and OK"),
            (912, 624, "Reasonable"),
            (960, 656, "Better Details"),
            (1072, 736, "Really Good"),
            (1136, 784, "Wan 2.2 Native"),
        ],
        "3:4": [
            (416, 544, "Fast Samples"),
            (560, 720, "Fast and OK"),
            (672, 864, "Reasonable"),
            (720, 912, "Better Details"),
            (784, 1008, "Really Good"),
            (848, 1088, "Wan 2.2 Native"),
        ],
        "4:3": [
            (544, 416, "Fast Samples"),
            (720, 560, "Fast and OK"),
            (864, 672, "Reasonable"),
            (912, 720, "Better Details"),
            (1008, 784, "Really Good"),
            (1088, 848, "Wan 2.2 Native"),
        ],
        "9:16": [
            (368, 624, "Fast Samples"),
            (480, 848, "Fast and OK"),
            (576, 1008, "Reasonable"),
            (608, 1072, "Better Details"),
            (672, 1184, "Really Good"),
            (720, 1264, "Wan 2.2 Native"),
        ],
        "16:9": [
            (624, 368, "Fast Samples"),
            (848, 480, "Fast and OK"),
            (1008, 576, "Reasonable"),
            (1072, 608, "Better Details"),
            (1184, 672, "Really Good"),
            (1264, 720, "Wan 2.2 Native"),
        ],
    }

    @classmethod
    def _rows_for(cls, aspect_ratio: str) -> List[Tuple[int, int, str]]:
        return cls.PRESETS.get(aspect_ratio) or cls.PRESETS[cls.FALLBACK_ASPECT]

    @classmethod
    def _labels_for(cls, aspect_ratio: str) -> List[str]:
        rows = cls._rows_for(aspect_ratio)
        return [f"{note} — {w}×{h}" for w, h, note in rows]

    @staticmethod
    def _legacy_note(note: str) -> str:
        if note == "Wan 2.2 Native":
            return "(WAN 2.2 native)"
        return note.lower()

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
    def _all_labels_for_validation(cls) -> List[str]:
        # Union across all aspect ratios so backend validation never rejects.
        seen = set()
        out = []
        for ar in cls.ASPECT_ORDER:
            for label in cls._labels_for(ar) + cls._legacy_labels_for(ar):
                if label not in seen:
                    seen.add(label)
                    out.append(label)
        return out

    @classmethod
    def INPUT_TYPES(cls):
        aspect_choices = list(cls.ASPECT_ORDER)
        default_ar = cls.FALLBACK_ASPECT
        all_resolution_choices = cls._all_labels_for_validation()
        default_res = cls._labels_for(default_ar)[0]

        return {
            "required": {
                "aspect_ratio": (aspect_choices, {"default": default_ar}),
                "resolution": (all_resolution_choices, {"default": default_res}),
                "round_to_16": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "image": ("IMAGE",),
            },
        }

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

        for i, (_, _, note) in enumerate(rows):
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
    def _round_to_multiple(value: float, multiple: int) -> int:
        if multiple <= 0:
            return int(round(value))
        return max(multiple, int(round(float(value) / float(multiple))) * multiple)

    @classmethod
    def _round_resolution_preserve_aspect(
        cls,
        width: int,
        height: int,
        multiple: int = 16,
    ) -> Tuple[int, int]:
        """
        Snap dimensions to a required multiple while keeping aspect ratio as close
        as possible to the requested width/height.
        """
        if width <= 0 or height <= 0:
            return (
                cls._round_to_multiple(max(1, width), multiple),
                cls._round_to_multiple(max(1, height), multiple),
            )

        target_ratio = float(width) / float(height)
        target_area = width * height

        base_w = cls._round_to_multiple(width, multiple)
        base_h = cls._round_to_multiple(height, multiple)

        width_candidates = {max(multiple, base_w + (step * multiple)) for step in range(-3, 4)}
        height_candidates = {max(multiple, base_h + (step * multiple)) for step in range(-3, 4)}

        candidates = set()

        # Generate options by preserving ratio from width and from height.
        for w in width_candidates:
            h = cls._round_to_multiple(float(w) / target_ratio, multiple)
            candidates.add((w, h))
        for h in height_candidates:
            w = cls._round_to_multiple(float(h) * target_ratio, multiple)
            candidates.add((w, h))

        # Add a small local grid around the nearest rounded size.
        for w in width_candidates:
            for h in height_candidates:
                candidates.add((w, h))

        best_w, best_h = min(
            candidates,
            key=lambda wh: (
                abs((float(wh[0]) / float(wh[1])) - target_ratio),
                abs(wh[0] - width) + abs(wh[1] - height),
                abs((wh[0] * wh[1]) - target_area),
            ),
        )
        return int(best_w), int(best_h)

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

        # Some graph contexts may wrap input tensors in a single-item list.
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
        round_to_16: bool = False,
    ):
        resolved_aspect = aspect_ratio
        image_dims = self._image_dimensions(image)
        image_w = None
        image_h = None
        if image_dims is not None:
            image_w, image_h = image_dims
            resolved_aspect = self._best_aspect_ratio(image_w, image_h)

        w, h = self._parse_resolution(resolved_aspect, resolution)
        resolved_resolution = self._label_for_dimensions(resolved_aspect, w, h) or resolution
        if round_to_16:
            w, h = self._round_resolution_preserve_aspect(w, h, multiple=16)

        result = (int(w), int(h))
        if image_dims is None:
            return result

        return {
            "ui": {
                "wanresolutions_state": [
                    {
                        "aspect_ratio": resolved_aspect,
                        "resolution": resolved_resolution,
                        "source_width": image_w,
                        "source_height": image_h,
                    }
                ]
            },
            "result": result,
        }
