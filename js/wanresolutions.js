import { app } from "../../scripts/app.js";

const NODE_CONFIGS = {
  WanResolutions: {
    fallbackAspect: "1:1",
    presets: {
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
        [576, 1024, "Fast Iteration"],
        [672, 1184, "Balanced"],
        [736, 1312, "HD Output"],
        [864, 1536, "High Detail"],
        [1056, 1888, "Full HD Output"],
      ],
      "16:9": [
        [512, 288, "Stage 1 Preview"],
        [1024, 576, "Fast Iteration"],
        [1184, 672, "Balanced"],
        [1312, 736, "HD Output"],
        [1536, 864, "High Detail"],
        [1888, 1056, "Full HD Output"],
      ],
    },
  },
};

const CONTEXT_MENU_SHIELD_KEY = "__wanresolutionsContextMenuShield";

function stopMenuEvent(event) {
  event.stopPropagation();
}

function shieldContextMenuRoot(root) {
  if (!root || root[CONTEXT_MENU_SHIELD_KEY]) return;

  Object.defineProperty(root, CONTEXT_MENU_SHIELD_KEY, {
    value: true,
    configurable: false,
    enumerable: false,
    writable: false,
  });

  root.addEventListener("pointerdown", stopMenuEvent);
  root.addEventListener("pointerup", stopMenuEvent);
  root.addEventListener("click", stopMenuEvent);
}

function installContextMenuShield() {
  const liteGraph = globalThis.LiteGraph;
  const OriginalContextMenu = liteGraph?.ContextMenu;
  if (!OriginalContextMenu || OriginalContextMenu[CONTEXT_MENU_SHIELD_KEY]) return;

  class ShieldedContextMenu extends OriginalContextMenu {
    constructor(values, options) {
      super(values, options);
      shieldContextMenuRoot(this.root);
    }
  }

  Object.defineProperty(ShieldedContextMenu, CONTEXT_MENU_SHIELD_KEY, {
    value: true,
    configurable: false,
    enumerable: false,
    writable: false,
  });

  liteGraph.ContextMenu = ShieldedContextMenu;
}

function configForNode(node) {
  return NODE_CONFIGS[node.comfyClass] ?? null;
}

function rowsFor(config, aspectRatio) {
  return config.presets[aspectRatio] ?? config.presets[config.fallbackAspect];
}

function labelsFor(config, aspectRatio) {
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
  const options = labelsFor(config, aspectRatio);
  const preferredResolution = preferred.resolution;
  const tierIdx = tierIndexForValue(config, aspectRatio, preferredResolution ?? resWidget.value);

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

function extractState(output) {
  const state =
    output?.aspect_resolution_state ??
    output?.wanresolutions_state;

  return Array.isArray(state) ? state[0] : state;
}

app.registerExtension({
  name: "aspectresolutions.dynamic_resolution_list",
  async setup() {
    installContextMenuShield();
  },

  async nodeCreated(node) {
    installContextMenuShield();

    const config = configForNode(node);
    if (!config) return;

    const { aspectWidget, resWidget } = getWidgets(node);
    if (!aspectWidget || !resWidget) return;

    const orig = aspectWidget.callback;
    aspectWidget.callback = (value) => {
      orig?.call(node, value);
      updateResolutionOptions(node, config, { aspectRatio: value });
    };

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
