# ComfyUI Video Resolutions

ComfyUI custom nodes that output `width` and `height` presets for Wan 2.2, MiniMax H3, and LTX video generation.

## Nodes

### `WanResolutions`

- Lets you choose an `aspect_ratio` and resolution quality tier (`Fast Draft`, `Preview`, `High Detail`, `Wan 2.2 Native`)
- Outputs `INT` values: `width`, `height`
- All sizes are divisible by 16 — the real alignment requirement for the Wan 2.2 A14B T2V/I2V models (8× VAE stride × 2× DiT patch), so no rounding flag is needed
- `Wan 2.2 Native` matches what the model actually targets (e.g. 16:9 → `1280×720`); the lower tiers are faster, lower-area conveniences
- Optional `IMAGE` input auto-matches the closest supported aspect ratio as an override
- Optional `official_only` restricts output to Wan's four official CLI buckets (`1280×720` / `720×1280` / `832×480` / `480×832`). Enabling it **swaps the resolution dropdown** to show just the two official sizes for the current orientation (`480P` / `720P`), so it's clear what is being filtered out; the current tier is mapped to the nearest bucket by area
- Keeps equivalent quality tier when you switch aspect ratios in the UI

### `LTXResolutions`

- Uses the same aspect-ratio workflow as `WanResolutions`
- Uses dimensions divisible by `32`
- Adds `image_bypass` so a connected `IMAGE` input can be ignored when needed
- Adds `upscaler_power` options for `none`, `x1.5`, and `x2`; upscale modes output the lower base resolution needed to reach the selected target tier
- The `upscaler_power` combo accepts a direct connection from the `LTX Upscaler Power` support node or any compatible generic/combo switch
- Preset tiers are tuned around current LTX 2.3 guidance:
  - official fast-iteration aspect sizes such as `640×640`, `512×768`, `768×512`, `512×704`, and `704×512`
  - the documented two-stage workflow, where lower preview passes feed higher output tiers
  - the current official landscape workflow pair of `960×544` base resolution and `1920×1088` x2 output
  - `720p` / `1080p`-class output targets, snapped to legal multiples of `32` and adapted per aspect ratio

### `MiniMax H3 Resolutions`

- Uses MiniMax H3's official T2V aspect ratios: `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, and `9:16`
- Provides six useful area buckets: `0.25 MP`, `0.40 MP`, `1K`, `1 MP`, `1.5K`, and `2K`
- Includes the official ComfyUI fast-preview anchor (`16:9` at `0.40 MP` → `864×480`) and base-quality anchor (`16:9` near `1 MP` → `1344×768`)
- Uses dimensions divisible by `32`, matching H3's effective transformer grid
- Without an `IMAGE`, outputs the selected T2V aspect-ratio preset
- With an `IMAGE`, switches to adaptive I2V sizing: it preserves the source image's ratio, targets the selected bucket's pixel area, and rounds both dimensions to the nearest multiple of `32`
- The `1K`, `1.5K`, and `2K` names use familiar `16:9` anchors; other ratios receive an area-equivalent size

### `LTX Upscaler Power`

- Outputs a connectable `COMBO` value: `none`, `x1.5`, or `x2`
- Connects directly to the `LTXResolutions.upscaler_power` combo, or can pass through a compatible generic/combo switch first

Supported aspect ratios for `WanResolutions` and `LTXResolutions`:

- `1:1`
- `2:3`
- `3:2`
- `3:4`
- `4:3`
- `9:16`
- `16:9`

`MiniMax H3 Resolutions` uses the official H3 T2V set:

- `1:1`
- `3:4`
- `4:3`
- `9:16`
- `16:9`
- `21:9`

## Installation

Clone into your ComfyUI `custom_nodes` directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/boobkake22/ComfyUI-WanResolutions.git
```

Restart ComfyUI after installing.

## Usage

1. Add `WanResolutions`, `MiniMax H3 Resolutions`, or `LTXResolutions`.
2. Pick `aspect_ratio` and `resolution`.
3. Optional: for `WanResolutions`, enable `official_only` to force one of Wan's four official buckets.
4. Optional: connect an `IMAGE` input. The H3 node preserves its exact aspect ratio with smart area sizing; the other nodes auto-select the nearest supported ratio.
5. Optional: on `LTXResolutions`, enable `image_bypass` to ignore the connected `IMAGE`.
6. Optional: select an `upscaler_power`, or connect `LTX Upscaler Power` directly to the `upscaler_power` combo.
7. Connect `width` and `height` outputs to your downstream nodes.

## Notes

- The LTX presets follow current LTX 2.3 notes rather than older `0.9.x` guidance. The documented anchor sizes are `640×640`, `512×768`, `768×512`, `512×704`, and `704×512`. Current official ComfyUI workflows use `960×544` before x2 spatial upscaling and `1920×1088` afterward.
- Upscaler modes treat the selected preset as the desired final target, round it upward to a factor-compatible legal size when necessary, and output a base resolution divisible by `32`.
- `WanResolutions` sizes are derived from Wan 2.2 A14B's true 16-pixel alignment grid: dense aspect ratios (`1:1`, `2:3`, `3:2`, `3:4`, `4:3`) land on exact ratios, and `16:9` / `9:16` sit within ~0.6% (sub-pixel) while keeping an even area ladder. `Wan 2.2 Native` reproduces the sizes Wan's own pipeline emits.
- MiniMax documents the open H3 Base model as a `768p` stage. Its official `2K` result uses a separate in-context regeneration stage that is not yet open-sourced. This node's `2K` entry supplies a direct, 32-aligned canvas size for local experimentation; it does not reproduce the unavailable H3-Regenerate-2K process.

## License

Apache-2.0. See `LICENSE`.
