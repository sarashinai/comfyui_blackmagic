# from server import PromptServer
# from aiohttp import web

class TextFormatter:
    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "formatText": ("STRING", {
                    "multiline": True,
                    "tooltip": "The text here will be reformatted.",
                    "placeholder": "This area processes text as you input it.",
                    }),
            },
            "optional": {
                "formattedText": ("STRING", {
                    "multiline": True,
                    "tooltip": "This is the formatted text.",
                    "placeholder": "This area is updated as you input text in the box above. This is the text that will be sent as output.",
                    }),
            }
        }

        return inputs
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted text",)
    FUNCTION = "FormatText"
    CATEGORY = "Black Magic/Text"
    OUTPUT_NODE = True
    DESCRIPTION = "Uses the builtin text formatting to format inputted text."
   
    def FormatText(self, formatText = None, formattedText = None):
        if (formattedText is not None):
            return (formattedText, )

        return ("", )