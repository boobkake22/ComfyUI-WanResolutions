# ComfyUI WanResolutions

ComfyUI custom nodes that output `width` and `height` presets for Wan 2.2 and LTX video generation.

## Nodes

### `WanResolutions`

- Lets you choose an `aspect_ratio` and resolution quality tier
- Outputs `INT` values: `width`, `height`
- Optional `IMAGE` input auto-matches the closest supported aspect ratio as an override
- Optional `round_to_16` snaps output to dimensions divisible by 16 while staying close to the target ratio
- Keeps equivalent quality tier when you switch aspect ratios in the UI

### `LTXResolutions`

- Uses the same aspect-ratio workflow as `WanResolutions`
- Uses dimensions divisible by `32`
- Omits `round_to_16`
- Adds `image_bypass` so a connected `IMAGE` input can be ignored when needed
- Preset tiers are tuned around current LTX 2.3 guidance:
  - official fast-iteration aspect sizes such as `640×640`, `512×768`, `768×512`, `512×704`, and `704×512`
  - the documented two-stage workflow, where lower preview passes feed higher output tiers
  - `720p` / `1080p`-class output targets, snapped to legal multiples of `32` and adapted per aspect ratio

Supported aspect ratios for both nodes:

- `1:1`
- `2:3`
- `3:2`
- `3:4`
- `4:3`
- `9:16`
- `16:9`

## Installation

Clone into your ComfyUI `custom_nodes` directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/boobkake22/ComfyUI-WanResolutions.git
```

Restart ComfyUI after installing.

## Usage

1. Add either `WanResolutions` or `LTXResolutions`.
2. Pick `aspect_ratio` and `resolution`.
3. Optional: for `WanResolutions`, enable `round_to_16`.
4. Optional: connect an `IMAGE` input to auto-select the nearest aspect ratio.
5. Optional: on `LTXResolutions`, enable `image_bypass` to ignore the connected `IMAGE`.
6. Connect `width` and `height` outputs to your downstream nodes.

## Notes

- The LTX presets now follow current LTX 2.3 notes rather than older `0.9.x` guidance. The documented anchor sizes are `640×640`, `512×768`, `768×512`, `512×704`, `704×512`, plus `1280×720` / `1920×1080` style target outputs in the multiscale workflows. This node converts those targets into aspect-based, `32`-divisible presets.
- `WanResolutions` keeps its existing Wan 2.2 preset table for backwards compatibility.

## License

Apache-2.0. See `LICENSE`.
