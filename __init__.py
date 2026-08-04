from .wanresolutions import (
    LTXResolutions,
    LTXUpscalerPower,
    MiniMaxH3Resolutions,
    WanResolutions,
)

NODE_CLASS_MAPPINGS = {
    "WanResolutions": WanResolutions,
    "MiniMaxH3Resolutions": MiniMaxH3Resolutions,
    "LTXResolutions": LTXResolutions,
    "LTXUpscalerPower": LTXUpscalerPower,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WanResolutions": "WanResolutions",
    "MiniMaxH3Resolutions": "MiniMax H3 Resolutions",
    "LTXResolutions": "LTXResolutions",
    "LTXUpscalerPower": "LTX Upscaler Power",
}

# Any .js files in this directory will be loaded by the frontend
WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
