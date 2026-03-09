# ComfyUI WanResolutions

ComfyUI custom node that outputs `width` and `height` presets for Wan 2.2 video generation.

## What it does

- Lets you choose an `aspect_ratio` and resolution quality tier
- Outputs `INT` values: `width`, `height`
- Optional `IMAGE` input auto-matches the closest supported aspect ratio as an override
- When an `IMAGE` input drives the aspect ratio during execution, the node updates the visible `aspect_ratio` and `resolution` widgets to match
- Optional `round_to_16` snaps output to dimensions divisible by 16 while staying close to the target ratio
- Keeps equivalent quality tier when you switch aspect ratios in the UI

Supported aspect ratios:

- `1:1`
- `2:3`
- `3:2`
- `3:4`
- `4:3`
- `9:16`
- `16:9`

Quality tiers per aspect ratio up to native Wan 2.2 quality.

## Installation

Clone into your ComfyUI `custom_nodes` directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/boobkake22/ComfyUI-WanResolutions.git
```

Restart ComfyUI after installing.

## Usage

1. Add the `WanResolutions` node.
2. Pick `aspect_ratio` and `resolution`.
3. Optional: enable `round_to_16` for dimensions divisible by 16.
4. Optional: connect an `IMAGE` input to auto-select the nearest aspect ratio.
5. Connect `width` and `height` outputs to your downstream nodes.

## License

Apache-2.0. See `LICENSE`.
