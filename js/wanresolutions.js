import { app } from "../../scripts/app.js";

const NODE_CONFIGS = {
  WanResolutions: {
    fallbackAspect: "1:1",
    officialSizes: [[1280, 720], [720, 1280], [832, 480], [480, 832]],
    presets: {
      "1:1": [
        [480, 480, "Fast Draft"],
        [640, 640, "Preview"],
        [832, 832, "High Detail"],
        [960, 960, "Wan 2.2 Native"],
      ],
      "2:3": [
        [384, 576, "Fast Draft"],
        [512, 768, "Preview"],
        [672, 1008, "High Detail"],
        [768, 1168, "Wan 2.2 Native"],
      ],
      "3:2": [
        [576, 384, "Fast Draft"],
        [768, 512, "Preview"],
        [1008, 672, "High Detail"],
        [1168, 768, "Wan 2.2 Native"],
      ],
      "3:4": [
        [432, 576, "Fast Draft"],
        [576, 768, "Preview"],
        [720, 960, "High Detail"],
        [816, 1104, "Wan 2.2 Native"],
      ],
      "4:3": [
        [576, 432, "Fast Draft"],
        [768, 576, "Preview"],
        [960, 720, "High Detail"],
        [1104, 816, "Wan 2.2 Native"],
      ],
      "9:16": [
        [352, 624, "Fast Draft"],
        [480, 848, "Preview"],
        [624, 1104, "High Detail"],
        [720, 1280, "Wan 2.2 Native"],
      ],
      "16:9": [
        [624, 352, "Fast Draft"],
        [848, 480, "Preview"],
        [1104, 624, "High Detail"],
        [1280, 720, "Wan 2.2 Native"],
      ],
    },
  },
  MiniMaxH3Resolutions: {
    fallbackAspect: "16:9",
    presets: {
      "1:1": [
        [512, 512, "Draft (0.25 MP)"],
        [640, 640, "Preview (0.40 MP)"],
        [768, 768, "1K (0.56 MP)"],
        [1024, 1024, "High Detail (1.00 MP)"],
        [1152, 1152, "1.5K (1.27 MP)"],
        [1536, 1536, "2K (2.25 MP)"],
      ],
      "3:4": [
        [448, 576, "Draft (0.25 MP)"],
        [576, 736, "Preview (0.40 MP)"],
        [672, 896, "1K (0.56 MP)"],
        [864, 1184, "High Detail (1.00 MP)"],
        [992, 1344, "1.5K (1.27 MP)"],
        [1344, 1760, "2K (2.25 MP)"],
      ],
      "4:3": [
        [576, 448, "Draft (0.25 MP)"],
        [736, 576, "Preview (0.40 MP)"],
        [896, 672, "1K (0.56 MP)"],
        [1184, 864, "High Detail (1.00 MP)"],
        [1344, 992, "1.5K (1.27 MP)"],
        [1760, 1344, "2K (2.25 MP)"],
      ],
      "9:16": [
        [384, 672, "Draft (0.25 MP)"],
        [480, 864, "Preview (0.40 MP)"],
        [576, 1024, "1K (0.56 MP)"],
        [768, 1344, "High Detail (1.00 MP)"],
        [864, 1536, "1.5K (1.27 MP)"],
        [1152, 2048, "2K (2.25 MP)"],
      ],
      "16:9": [
        [672, 384, "Draft (0.25 MP)"],
        [864, 480, "Preview (0.40 MP)"],
        [1024, 576, "1K (0.56 MP)"],
        [1344, 768, "High Detail (1.00 MP)"],
        [1536, 864, "1.5K (1.27 MP)"],
        [2048, 1152, "2K (2.25 MP)"],
      ],
      "21:9": [
        [768, 320, "Draft (0.25 MP)"],
        [992, 416, "Preview (0.40 MP)"],
        [1184, 512, "1K (0.56 MP)"],
        [1536, 672, "High Detail (1.00 MP)"],
        [1760, 768, "1.5K (1.27 MP)"],
        [2336, 992, "2K (2.25 MP)"],
      ],
    },
  },
  LTXResolutions: {
    fallbackAspect: "1:1",
    presets: {
      "1:1": [
        [320, 320, "Stage 1 Preview"],
        [640, 640, "Fast Iteration"],
        [768, 768, "Balanced"],
        [960, 960, "HD Output"],
        [1184, 1184, "High Detail"],
        [1440, 1440, "Full HD Output"],
      ],
      "2:3": [
        [256, 384, "Stage 1 Preview"],
        [512, 768, "Fast Iteration"],
        [640, 960, "Balanced"],
        [768, 1152, "HD Output"],
        [960, 1440, "High Detail"],
        [1152, 1728, "Full HD Output"],
      ],
      "3:2": [
        [384, 256, "Stage 1 Preview"],
        [768, 512, "Fast Iteration"],
        [960, 640, "Balanced"],
        [1152, 768, "HD Output"],
        [1440, 960, "High Detail"],
        [1728, 1152, "Full HD Output"],
      ],
      "3:4": [
        [256, 352, "Stage 1 Preview"],
        [512, 704, "Fast Iteration"],
        [640, 864, "Balanced"],
        [864, 1152, "HD Output"],
        [1056, 1408, "High Detail"],
        [1248, 1664, "Full HD Output"],
      ],
      "4:3": [
        [352, 256, "Stage 1 Preview"],
        [704, 512, "Fast Iteration"],
        [864, 640, "Balanced"],
        [1152, 864, "HD Output"],
        [1408, 1056, "High Detail"],
        [1664, 1248, "Full HD Output"],
      ],
      "9:16": [
        [288, 512, "Stage 1 Preview"],
        [544, 960, "Fast Iteration"],
        [672, 1184, "Balanced"],
        [736, 1312, "HD Output"],
        [864, 1536, "High Detail"],
        [1088, 1920, "Full HD Output"],
      ],
      "16:9": [
        [512, 288, "Stage 1 Preview"],
        [960, 544, "Fast Iteration"],
        [1184, 672, "Balanced"],
        [1312, 736, "HD Output"],
        [1536, 864, "High Detail"],
        [1920, 1088, "Full HD Output"],
      ],
    },
  },
};

const OPEN_MENU_SELECTORS = [
  ".litegraph.litecontextmenu",
  ".litecontextmenu",
  ".p-popover",
  "[data-pc-name='popover']",
];
const MENU_INTERACTION_TRACKER_KEY = "__wanresolutionsMenuInteractionTracker";
const MENU_INTERACTION_WINDOW_MS = 300;
const TOGGLE_GUARD_WIDGET_NAMES = ["official_only", "image_bypass"];
let lastMenuInteractionAt = 0;

function hasOpenMenu() {
  return OPEN_MENU_SELECTORS.some((selector) => document.querySelector(selector));
}

function noteMenuInteraction() {
  lastMenuInteractionAt = performance.now();
}

function recentMenuInteraction() {
  return (performance.now() - lastMenuInteractionAt) <= MENU_INTERACTION_WINDOW_MS;
}

function installMenuInteractionTracker() {
  if (document[MENU_INTERACTION_TRACKER_KEY]) return;

  Object.defineProperty(document, MENU_INTERACTION_TRACKER_KEY, {
    value: true,
    configurable: false,
    enumerable: false,
    writable: false,
  });

  const trackMenuInteraction = (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;
    if (!target.closest(OPEN_MENU_SELECTORS.join(","))) return;
    noteMenuInteraction();
  };

  document.addEventListener("pointerdown", trackMenuInteraction, true);
  document.addEventListener("pointerup", trackMenuInteraction, true);
  document.addEventListener("click", trackMenuInteraction, true);
}

function guardPointerDown(widget, shouldBlock) {
  if (!widget) return;

  const original = widget.onPointerDown;
  widget.onPointerDown = function (pointer, node, canvas) {
    if (shouldBlock(pointer, node, canvas)) return true;
    return original?.call(this, pointer, node, canvas) ?? false;
  };
}

function guardWidgetHitTesting(node, shouldBlock) {
  const original = node.getWidgetOnPos;
  if (typeof original !== "function") return;

  node.getWidgetOnPos = function (...args) {
    const widget = original.apply(this, args);
    if (widget && TOGGLE_GUARD_WIDGET_NAMES.includes(widget.name) && shouldBlock()) {
      return null;
    }
    return widget;
  };
}

function configForNode(node) {
  return NODE_CONFIGS[node.comfyClass] ?? null;
}

function rowsFor(config, aspectRatio) {
  return config.presets[aspectRatio] ?? config.presets[config.fallbackAspect];
}

function aspectIsLandscape(aspectRatio) {
  const m = /^\s*(\d+)\s*:\s*(\d+)\s*$/.exec(aspectRatio || "");
  if (!m) return true;
  return parseInt(m[1], 10) >= parseInt(m[2], 10);
}

function officialLabelsFor(config, aspectRatio) {
  if (!config.officialSizes) return [];
  const landscape = aspectIsLandscape(aspectRatio);
  const pool = config.officialSizes.filter(([w, h]) => (w >= h) === landscape);
  return (pool.length ? pool : config.officialSizes)
    .slice()
    .sort((a, b) => a[0] * a[1] - b[0] * b[1])
    .map(([w, h]) => `Official ${Math.min(w, h)}P — ${w}×${h}`);
}

function labelsFor(config, aspectRatio, officialOnly) {
  if (officialOnly && config.officialSizes) return officialLabelsFor(config, aspectRatio);
  const rows = rowsFor(config, aspectRatio);
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

function tierIndexForValue(config, aspectRatio, value) {
  const rows = rowsFor(config, aspectRatio);
  const normalizedValue = normalizeText(value);

  const noteMatches = rows
    .map((row, index) => ({ row, index }))
    .sort((a, b) => normalizeText(b.row[2]).length - normalizeText(a.row[2]).length);
  const noteMatch = noteMatches.find(({ row }) => {
    const normalizedNote = normalizeText(row[2]);
    return normalizedNote && normalizedValue.includes(normalizedNote);
  });
  if (noteMatch) return noteMatch.index;

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

function officialOnlyWidget(node) {
  return node.widgets?.find((w) => w.name === "official_only");
}

function isOfficialOnly(node) {
  const widget = officialOnlyWidget(node);
  if (!widget) return false;
  return Boolean(widgetValue(node, widget) ?? widget.value);
}

function sizeForLabel(config, aspectRatio, value) {
  const parsed = parseSize(value);
  if (parsed) return parsed;
  const rows = rowsFor(config, aspectRatio);
  const row = rows[tierIndexForValue(config, aspectRatio, value)] ?? rows[0];
  return { w: row[0], h: row[1] };
}

function nearestOption(options, target) {
  if (!target) return options[0];
  let best = options[0];
  let bestDelta = Infinity;
  for (const opt of options) {
    const size = parseSize(opt);
    if (!size) continue;
    const delta = Math.abs(size.w * size.h - target.w * target.h);
    if (delta < bestDelta) {
      bestDelta = delta;
      best = opt;
    }
  }
  return best;
}

function widgetValue(node, widget) {
  if (!widget) return undefined;

  const index = node.widgets?.indexOf(widget) ?? -1;
  if (index >= 0 && Array.isArray(node.widgets_values)) {
    const savedValue = node.widgets_values[index];
    if (savedValue != null) return savedValue;
  }

  return widget.value;
}

function preferredSelections(node, config) {
  const { aspectWidget, resWidget } = getWidgets(node);
  return {
    aspectRatio: widgetValue(node, aspectWidget) ?? config.fallbackAspect,
    resolution: widgetValue(node, resWidget),
  };
}

function syncWidgetValues(node) {
  if (!Array.isArray(node.widgets_values) || !Array.isArray(node.widgets)) return;
  node.widgets.forEach((widget, index) => {
    node.widgets_values[index] = widget.value;
  });
}

function updateResolutionOptions(node, config, preferred = {}) {
  const { aspectWidget, resWidget } = getWidgets(node);
  if (!aspectWidget || !resWidget) return;

  const aspectRatio = preferred.aspectRatio ?? aspectWidget.value ?? config.fallbackAspect;
  const officialOnly = preferred.officialOnly ?? isOfficialOnly(node);
  const options = labelsFor(config, aspectRatio, officialOnly);
  const preferredResolution = preferred.resolution;
  const currentValue = preferredResolution ?? resWidget.value;

  let nextValue;
  if (preferredResolution && options.includes(preferredResolution)) {
    nextValue = preferredResolution;
  } else if (currentValue && options.includes(currentValue)) {
    nextValue = currentValue;
  } else {
    // Map across lists (aspect change, or official_only toggle) by nearest area
    // so the equivalent tier / bucket stays selected.
    nextValue = nearestOption(options, sizeForLabel(config, aspectRatio, currentValue)) ?? options[0];
  }

  aspectWidget.value = aspectRatio;
  resWidget.options = resWidget.options ?? {};
  resWidget.options.values = options;
  resWidget.value = nextValue;

  syncWidgetValues(node);
  node.setDirtyCanvas(true, true);
}

function extractState(output) {
  const state =
    output?.aspect_resolution_state ??
    output?.wanresolutions_state;

  return Array.isArray(state) ? state[0] : state;
}

app.registerExtension({
  name: "aspectresolutions.dynamic_resolution_list",
  async nodeCreated(node) {
    installMenuInteractionTracker();

    const config = configForNode(node);
    if (!config) return;

    const { aspectWidget, resWidget } = getWidgets(node);
    if (!aspectWidget || !resWidget) return;

    guardWidgetHitTesting(node, () => hasOpenMenu() || recentMenuInteraction());

    for (const widget of node.widgets ?? []) {
      if (!TOGGLE_GUARD_WIDGET_NAMES.includes(widget.name)) continue;
      guardPointerDown(widget, () => hasOpenMenu() || recentMenuInteraction());
    }

    const orig = aspectWidget.callback;
    aspectWidget.callback = (value) => {
      orig?.call(node, value);
      updateResolutionOptions(node, config, { aspectRatio: value });
    };

    const officialWidget = officialOnlyWidget(node);
    if (officialWidget) {
      const origOfficial = officialWidget.callback;
      officialWidget.callback = (value) => {
        origOfficial?.call(node, value);
        updateResolutionOptions(node, config, { officialOnly: Boolean(value) });
      };
    }

    const onExecuted = node.onExecuted;
    node.onExecuted = function (output) {
      onExecuted?.call(this, output);

      const state = extractState(output);
      if (!state) return;

      updateResolutionOptions(this, config, {
        aspectRatio: state.aspect_ratio,
        resolution: state.resolution,
      });
    };

    updateResolutionOptions(node, config, preferredSelections(node, config));
  },

  loadedGraphNode(node) {
    const config = configForNode(node);
    if (!config) return;

    updateResolutionOptions(node, config, preferredSelections(node, config));
  },
});
