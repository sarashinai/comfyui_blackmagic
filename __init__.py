"""
Top-level package for comfyui_blackmagic.
@author: sarashinai
@title: Black Magic
@nickname: sarashinai
@description: A collection of ComfyUI nodes I created to solve specific issues I was having.
"""

__author__ = """sarashinai"""
__email__ = "sarashinai@gmail.com"
__version__ = "0.0.1"

from .py.text_lora_multiloader import TextLoraMultiloader
from .py.text_formatter import TextFormatter

NODE_CLASS_MAPPINGS = {
    "TextLoraMultiloader": TextLoraMultiloader,
    "TextFormatter": TextFormatter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextLoraMultiloader": "Load LORAs by instruction",
    "TextFormatter": "Use ComfyUI to format text",
}

WEB_DIRECTORY = "./js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

print(f'\33[92mBLACK MAGIC: 2 nodes added to the cauldron.\33[00m');

