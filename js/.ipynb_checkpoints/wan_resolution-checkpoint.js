import { app } from "../../scripts/app.js";

const PRESETS = {
  "1:1": [
    "1. 480×480 — fast samples",
    "2. 640×640 — fast and ok",
    "3. 768×768 — reasonable",
    "4. 800×800 — better details",
    "5. 880×880 — really good",
    "6. 960×960 — (WAN 2.2 native)",
  ],
  "3:4": [
    "1. 416×544 — fast samples",
    "2. 560×720 — fast and ok",
    "3. 672×864 — reasonable",
    "4. 720×912 — better details",
    "5. 784×1008 — really good",
    "6. 848×1088 — (WAN 2.2 native)",
  ],
  "2:3": [
    "1. 384×576 — fast samples",
    "2. 528×768 — fast and ok",
    "3. 624×912 — reasonable",
    "4. 656×960 — better details",
    "5. 736×1072 — really good",
    "6. 784×1136 — (WAN 2.2 native)",
  ],
  "9:16": [
    "1. 368×624 — fast samples",
    "2. 480×848 — fast and ok",
    "3. 576×1008 — reasonable",
    "4. 608×1072 — better details",
    "5. 672×1184 — really good",
    "6. 720×1264 — (WAN 2.2 native)",
  ],
};

function leadingIndex(str) {
  const m = /^\s*(\d+)\s*[\.\)]/.exec(str || "");
  return m ? parseInt(m[1], 10) : null;
}

app.registerExtension({
  name: "wan_resolution.dynamic_resolution_list",
  async nodeCreated(node) {
    if (node.comfyClass !== "WanResolution") return;

    const aspectWidget = node.widgets?.find((w) => w.name === "aspect_ratio");
    const resWidget = node.widgets?.find((w) => w.name === "resolution");
    if (!aspectWidget || !resWidget) return;

    const updateResolutionOptions = () => {
      const ar = aspectWidget.value;
      const options = PRESETS[ar] ?? PRESETS["1:1"];

      // Try to keep the same tier number (1..6) when switching aspect ratios
      const prevIdx = leadingIndex(resWidget.value);
      resWidget.options.values = options;

      if (prevIdx != null) {
        const candidate = options.find((v) => leadingIndex(v) === prevIdx);
        resWidget.value = candidate ?? options[0];
      } else if (!options.includes(resWidget.value)) {
        resWidget.value = options[0];
      }

      node.setDirtyCanvas(true, true);
    };

    // Hook AR dropdown change
    const orig = aspectWidget.callback;
    aspectWidget.callback = (value) => {
      orig?.call(node, value);
      updateResolutionOptions();
    };

    // Initialize once on creation (and when loading workflows)
    updateResolutionOptions();
  },
});