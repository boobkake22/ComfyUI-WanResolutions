from .wanresolutions import LTXResolutions, WanResolutions

NODE_CLASS_MAPPINGS = {
    "WanResolutions": WanResolutions,
    "LTXResolutions": LTXResolutions,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WanResolutions": "WanResolutions",
    "LTXResolutions": "LTXResolutions",
}

# Any .js files in this directory will be loaded by the frontend
WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
