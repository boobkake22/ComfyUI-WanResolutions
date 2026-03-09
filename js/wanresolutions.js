import { app } from "../../scripts/app.js";

const PRESETS = {
  "1:1": [
    [480, 480, "Fast Samples"],
    [640, 640, "Fast and OK"],
    [768, 768, "Reasonable"],
    [800, 800, "Better Details"],
    [880, 880, "Really Good"],
    [960, 960, "Wan 2.2 Native"],
  ],
  "2:3": [
    [384, 576, "Fast Samples"],
    [528, 768, "Fast and OK"],
    [624, 912, "Reasonable"],
    [656, 960, "Better Details"],
    [736, 1072, "Really Good"],
    [784, 1136, "Wan 2.2 Native"],
  ],
  "3:2": [
    [576, 384, "Fast Samples"],
    [768, 528, "Fast and OK"],
    [912, 624, "Reasonable"],
    [960, 656, "Better Details"],
    [1072, 736, "Really Good"],
    [1136, 784, "Wan 2.2 Native"],
  ],
  "3:4": [
    [416, 544, "Fast Samples"],
    [560, 720, "Fast and OK"],
    [672, 864, "Reasonable"],
    [720, 912, "Better Details"],
    [784, 1008, "Really Good"],
    [848, 1088, "Wan 2.2 Native"],
  ],
  "4:3": [
    [544, 416, "Fast Samples"],
    [720, 560, "Fast and OK"],
    [864, 672, "Reasonable"],
    [912, 720, "Better Details"],
    [1008, 784, "Really Good"],
    [1088, 848, "Wan 2.2 Native"],
  ],
  "9:16": [
    [368, 624, "Fast Samples"],
    [480, 848, "Fast and OK"],
    [576, 1008, "Reasonable"],
    [608, 1072, "Better Details"],
    [672, 1184, "Really Good"],
    [720, 1264, "Wan 2.2 Native"],
  ],
  "16:9": [
    [624, 368, "Fast Samples"],
    [848, 480, "Fast and OK"],
    [1008, 576, "Reasonable"],
    [1072, 608, "Better Details"],
    [1184, 672, "Really Good"],
    [1264, 720, "Wan 2.2 Native"],
  ],
};

const FALLBACK_ASPECT = "1:1";

function rowsFor(aspectRatio) {
  return PRESETS[aspectRatio] ?? PRESETS[FALLBACK_ASPECT];
}

function labelsFor(aspectRatio) {
  const rows = rowsFor(aspectRatio);
  return rows.map(([w, h, note]) => `${note} — ${w}×${h}`);
}

function leadingIndex(str) {
  const m = /^\s*(\d+)\s*[\.\)]/.exec(str || "");
  return m ? parseInt(m[1], 10) : null;
}

function normalizeText(str) {
  return (str || "")
    .toLowerCase()
    .replaceAll(/[()]/g, "")
    .replaceAll(/\s+/g, " ")
    .trim();
}

function parseSize(str) {
  const normalized = (str || "").replaceAll("×", "x");
  const m = /(\d+)\s*x\s*(\d+)/i.exec(normalized);
  if (!m) return null;
  return { w: parseInt(m[1], 10), h: parseInt(m[2], 10) };
}

function tierIndexForValue(aspectRatio, value) {
  const rows = rowsFor(aspectRatio);
  const normalizedValue = normalizeText(value);

  const noteMatch = rows.findIndex(([, , note]) => {
    const normalizedNote = normalizeText(note);
    return normalizedNote && normalizedValue.includes(normalizedNote);
  });
  if (noteMatch >= 0) return noteMatch;

  const idx = leadingIndex(value);
  if (idx != null) {
    return Math.max(0, Math.min(idx - 1, rows.length - 1));
  }

  const size = parseSize(value);
  if (size) {
    const match = rows.findIndex(([w, h]) => w === size.w && h === size.h);
    if (match >= 0) return match;
  }

  return 0;
}

function getWidgets(node) {
  const aspectWidget = node.widgets?.find((w) => w.name === "aspect_ratio");
  const resWidget = node.widgets?.find((w) => w.name === "resolution");
  return { aspectWidget, resWidget };
}

function syncWidgetValues(node) {
  if (!Array.isArray(node.widgets_values) || !Array.isArray(node.widgets)) return;
  node.widgets.forEach((widget, index) => {
    node.widgets_values[index] = widget.value;
  });
}

function updateResolutionOptions(node, preferred = {}) {
  const { aspectWidget, resWidget } = getWidgets(node);
  if (!aspectWidget || !resWidget) return;

  const aspectRatio = preferred.aspectRatio ?? aspectWidget.value ?? FALLBACK_ASPECT;
  const options = labelsFor(aspectRatio);
  const preferredResolution = preferred.resolution;
  const tierIdx = tierIndexForValue(aspectRatio, preferredResolution ?? resWidget.value);

  aspectWidget.value = aspectRatio;
  resWidget.options = resWidget.options ?? {};
  resWidget.options.values = options;
  resWidget.value =
    preferredResolution && options.includes(preferredResolution)
      ? preferredResolution
      : (options[tierIdx] ?? options[0]);

  syncWidgetValues(node);
  node.setDirtyCanvas(true, true);
}

app.registerExtension({
  name: "wanresolutions.dynamic_resolution_list",
  async nodeCreated(node) {
    if (node.comfyClass !== "WanResolutions") return;

    const { aspectWidget, resWidget } = getWidgets(node);
    if (!aspectWidget || !resWidget) return;

    // Hook AR dropdown change
    const orig = aspectWidget.callback;
    aspectWidget.callback = (value) => {
      orig?.call(node, value);
      updateResolutionOptions(node, { aspectRatio: value });
    };

    const onExecuted = node.onExecuted;
    node.onExecuted = function (output) {
      onExecuted?.call(this, output);

      const state = output?.wanresolutions_state;
      if (!state) return;

      updateResolutionOptions(this, {
        aspectRatio: state.aspect_ratio,
        resolution: state.resolution,
      });
    };

    // Initialize once on creation (and when loading workflows)
    updateResolutionOptions(node);
  },
});
