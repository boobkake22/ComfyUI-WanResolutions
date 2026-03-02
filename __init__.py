from .wan_resolution import WanResolution

NODE_CLASS_MAPPINGS = {
    "WanResolution": WanResolution,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WanResolution": "Wan Resolution",
}

# Any .js files in this directory will be loaded by the frontend
WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]