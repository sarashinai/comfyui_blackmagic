import folder_paths
import os
import torch
from typing import Dict
from nodes import LoraLoader
# from server import PromptServer
# from aiohttp import web

block_types = ["all", "single_blocks", "double_blocks"]

class TextLoraMultiloader:
    def __init__(self):
      # Add loaders and blocks to a set of arrays for future expansion
      self.loaded_lora = None
    
    @classmethod
    def INPUT_TYPES(self):
        inputs = {
            "required": {
                "model": ("MODEL", {"forceInput": True}),
                "instructions": ("STRING", {
                    "multiline": True,
                    "tooltip": "The instructions here are passed to the LORA loader. All black lines and lines starting with # are ignored."
                    }),
            },
            "optional": {
                "clip": ("CLIP", {"forceInput": True}),
                "lora": (folder_paths.get_filename_list("loras"),),
                "lora_strength": ("FLOAT", {
                                "default": 1.0,
                                "min": -10.0,
                                "max": 10.0,
                                "step": 0.01}),
                "loader": (["cgthree", "facok"],),
                "clip_strength": ("FLOAT", {
                                "default": 1.0,
                                "min": -10.0,
                                "max": 10.0,
                                "step": 0.01}),
                "blocks": (block_types,),
            }
        }

        return inputs
    
    RETURN_TYPES = ("MODEL", "CLIP",)
    # RETURN_NAMES = ("MODEL", "CLIP",)
    FUNCTION = "ProcessTextAndLoadLoras"
    CATEGORY = "Black Magic/LORA"
    OUTPUT_NODE = True
    DESCRIPTION = "Uses multiline text instructions to control LORA loading."

    def convert_key_format(self, key: str) -> str:
        """转换LoRA key格式,支持多种命名方式"""
        # 移除可能的前缀
        prefixes = ["diffusion_model.", "transformer."]
        for prefix in prefixes:
            if key.startswith(prefix):
                key = key[len(prefix):]
                break
                
        return key

    def filter_lora_keys(self, lora: Dict[str, torch.Tensor], blocks_type: str) -> Dict[str, torch.Tensor]:
        """根据blocks类型过滤LoRA权重"""
        if blocks_type == "all":
            return lora
            
        filtered_lora = {}
        for key, value in lora.items():
            base_key = self.convert_key_format(key)
            
            # 检查是否包含目标block
            if blocks_type == "single_blocks" in base_key:
                filtered_lora[key] = value
            elif blocks_type == "double_blocks" in base_key:
                filtered_lora[key] = value
                
        return filtered_lora

    def check_for_musubi(self, lora: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Checks for and converts from Musubi Tuner format which supports Network Alpha and uses different naming. Largely copied from that project"""
        prefix = "lora_unet_"
        musubi = False
        lora_alphas = {}
        for key, value in lora.items():
            if key.startswith(prefix):
                lora_name = key.split(".", 1)[0]  # before first dot
                if lora_name not in lora_alphas and "alpha" in key:
                    lora_alphas[lora_name] = value
                    musubi = True
        if musubi:
            # print("Loading Musubi Tuner format LoRA...")
            converted_lora = {}
            for key, weight in lora.items():
                if key.startswith(prefix):
                    if "alpha" in key:
                        continue
                lora_name = key.split(".", 1)[0]  # before first dot
                # HunyuanVideo lora name to module name: ugly but works
                module_name = lora_name[len(prefix) :]  # remove "lora_unet_"
                module_name = module_name.replace("_", ".")  # replace "_" with "."
                module_name = module_name.replace("double.blocks.", "double_blocks.")  # fix double blocks
                module_name = module_name.replace("single.blocks.", "single_blocks.")  # fix single blocks
                module_name = module_name.replace("img.", "img_")  # fix img
                module_name = module_name.replace("txt.", "txt_")  # fix txt
                module_name = module_name.replace("attn.", "attn_")  # fix attn
                diffusers_prefix = "diffusion_model"
                if "lora_down" in key:
                    new_key = f"{diffusers_prefix}.{module_name}.lora_A.weight"
                    dim = weight.shape[0]
                elif "lora_up" in key:
                    new_key = f"{diffusers_prefix}.{module_name}.lora_B.weight"
                    dim = weight.shape[1]
                else:
                    print(f"unexpected key: {key} in Musubi LoRA format")
                    continue
                # scale weight by alpha
                if lora_name in lora_alphas:
                    # we scale both down and up, so scale is sqrt
                    scale = lora_alphas[lora_name] / dim
                    scale = scale.sqrt()
                    weight = weight * scale
                else:
                    print(f"missing alpha for {lora_name}")

                converted_lora[new_key] = weight
            return converted_lora
        else:
            # print("Loading Diffusers format LoRA...")
            return lora

    def load_facok_lora(self, model, lora_name: str, strength: float, blocks_type: str):
        """
        加载并应用LoRA到模型
        
        Parameters
        ----------
        model : ModelPatcher
            要应用LoRA的基础模型
        lora_name : str
            LoRA文件名
        strength : float
            LoRA权重强度
        blocks_type : str
            要加载的blocks类型: "all", "single_blocks" 或 "double_blocks"
            
        Returns
        -------
        tuple
            包含应用了LoRA的模型的元组
        """
        if not lora_name:
            return (model,)
            
        from comfy.utils import load_torch_file
        from comfy.sd import load_lora_for_models
        from comfy.lora import load_lora

        # 获取LoRA文件路径
        lora_path = folder_paths.get_full_path("loras", lora_name)
        if not os.path.exists(lora_path):
            raise Exception(f"Lora {lora_name} not found at {lora_path}")

        # 缓存LoRA加载
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
            else:
                self.loaded_lora = None
        
        if self.loaded_lora is None:
            lora = load_torch_file(lora_path)
            self.loaded_lora = (lora_path, lora)
        
        diffusers_lora = self.check_for_musubi(lora)
        # 过滤并转换LoRA权重
        filtered_lora = self.filter_lora_keys(diffusers_lora, blocks_type)
        
        # 应用LoRA
        new_model, _ = load_lora_for_models(model, None, filtered_lora, strength, 0)
        if new_model is not None:
            return (new_model,)
            
        return (model,)
    
    # pylint: disable = too-many-return-statements, too-many-branches
    def get_lora_by_filename(self, file_path, lora_paths=None, log_node=None):
        """Returns a lora by filename, looking for exactl paths and then fuzzier matching."""
        lora_paths = lora_paths if lora_paths is not None else folder_paths.get_filename_list('loras')

        if file_path in lora_paths:
            return file_path

        lora_paths_no_ext = [os.path.splitext(x)[0] for x in lora_paths]

        # See if we've entered the exact path, but without the extension
        if file_path in lora_paths_no_ext:
            found = lora_paths[lora_paths_no_ext.index(file_path)]
            return found

        # Same check, but ensure file_path is without extension.
        file_path_force_no_ext = os.path.splitext(file_path)[0]
        if file_path_force_no_ext in lora_paths_no_ext:
            found = lora_paths[lora_paths_no_ext.index(file_path_force_no_ext)]
            return found

        # See if we passed just the name, without paths.
        lora_filenames_only = [os.path.basename(x) for x in lora_paths]
        if file_path in lora_filenames_only:
            found = lora_paths[lora_filenames_only.index(file_path)]
            if log_node is not None:
                print(f'Matched Lora input "{file_path}" to "{found}".')
                return found

        # Same, but force the input to be without paths
        file_path_force_filename = os.path.basename(file_path)
        lora_filenames_only = [os.path.basename(x) for x in lora_paths]
        if file_path_force_filename in lora_filenames_only:
            found = lora_paths[lora_filenames_only.index(file_path_force_filename)]
            if log_node is not None:
                print(f'Matched Lora input "{file_path}" to "{found}".')
                return found

        # Check the filenames and without extension.
        lora_filenames_and_no_ext = [os.path.splitext(os.path.basename(x))[0] for x in lora_paths]
        if file_path in lora_filenames_and_no_ext:
            found = lora_paths[lora_filenames_and_no_ext.index(file_path)]
            if log_node is not None:
                print(f'Matched Lora input "{file_path}" to "{found}".')
                return found

        # And, one last forcing the input to be the same
        file_path_force_filename_and_no_ext = os.path.splitext(os.path.basename(file_path))[0]
        if file_path_force_filename_and_no_ext in lora_filenames_and_no_ext:
            found = lora_paths[lora_filenames_and_no_ext.index(file_path_force_filename_and_no_ext)]
            if log_node is not None:
                print(f'Matched Lora input "{file_path}" to "{found}".')
                return found

        # Finally, super fuzzy, we'll just check if the input exists in the path at all.
        for index, lora_path in enumerate(lora_paths):
            if file_path in lora_path:
                found = lora_paths[index]
                if log_node is not None:
                    print(f'Fuzzy-matched Lora input "{file_path}" to "{found}".')
                return found

        if log_node is not None:
            print(f'Lora "{file_path}" not found, skipping.')

        return None

    def load_cgthree_lora(self, model, clip, lora_name, lora_strength, clip_strength):
        lora = self.get_lora_by_filename(lora_name)

        if lora is not None:
            model, clip = LoraLoader().load_lora(model, clip, lora, lora_strength, clip_strength)

        return (model, clip)

    def ProcessTextAndLoadLoras(self, model, instructions, clip = None, lora = None, lora_strength = None, clip_strength = None, loader = None, blocks = None):
        if (len(instructions) != 0):
            # print('Instructions: "{0}"'.format(instructions))

            instructionList = instructions.split("\n")

            for line in instructionList:
                if (len(line) != 0):
                    if (line[0] == '#'): # Skip commented lines
                        continue

                    # print(line)

                    line = line.strip()

                    info = line.split(" | ")

                    lora = info[0].strip()
                    lora_strength = float(info[1].strip())

                    match (info[2].strip()):
                        case "cgthree":
                            clip_strength = float(info[3].strip())

                            print(f'TextLoraMultiloader: Loading {lora} (cgthree, LS = {lora_strength},  CS = {clip_strength})...')

                            model, clip = self.load_cgthree_lora(model, clip, lora, lora_strength, clip_strength)
                        case "facok":
                            blocks = info[3].strip()

                            print(f'TextLoraMultiloader: Loading {lora} (facok, LS = {lora_strength}, {blocks})...')

                            model, = self.load_facok_lora(model, lora, lora_strength, blocks)

        return (model, clip, )
    
    # @classmethod
    # def VALIDATE_INPUTS(self, input_types, **kwargs):
    #      return "IT'S ALL WRONG!"

    @classmethod
    def VALIDATE_INPUTS(self, input_types, **kwargs):
        # {'model': 'MODEL', 'clip': 'CLIP'}
        # {
        #     'instructions': 'LORA.safetensors | 1 | cgthree | 4\nLORA.safetensors | 7 | cgthree | 4', 
        #     'lora': 'LORA.safetensors',
        #     'lora_strength': 7.0, 
        #     'loader': 'cgthree', 
        #     'clip_strength': 4.0, 
        #     'model': None, 
        #     'clip': None
        # }
        # print(input_types)
        # print(kwargs)

        # print(block_types);

        returnString = "TextLoraMultiloader: Check ComfyUI console for detailed error message."

        if "model" not in input_types or input_types["model"] == None:
            print("!!! TextLoraMultiloader error !!! MODEL must be provided.")
                            
            return returnString

        instructions = kwargs["instructions"]
        
        if (len(instructions) != 0):
            self.tokens = []
            # print('Instructions: "{0}"'.format(instructions))

            instructionList = instructions.split("\n")

            index = 1

            for line in instructionList:
                if (len(line) != 0):
                    if (line[0] == '#'): # Skip commented lines
                        continue
                    # print("{0}: {1}".format(index, line))
                    
                    line = line.strip()

                    info = line.split(" | ")

                    # print(info)
                    # print(len(info))

                    if (len(info) == 4):
                        if (len(info[0]) == 0):
                            print("!!! TextLoraMultiloader formatting error !!! Missing LORA.\n\nLine {0}: {1}".format(index, line))
                            
                            return returnString
                                                                                        
                        if (info[0].find(".safetensors") == -1):
                            print('!!! TextLoraMultiloader formatting error !!! LORA must be formatted as "FULLNAME.safetensors"{1}\nLine {0}: {1}'.format(index, line))
                            
                            return returnString

                        if (len(info[1]) == 0):
                            print('!!! TextLoraMultiloader formatting error !!! Missing LORA strength.\nLine {0}: {1}'.format(index, line))
                            
                            return returnString

                        # console.log(parseFloat(info[1]));

                        try:
                            float(info[1].strip())
                        except ValueError as e:
                            print('!!! TextLoraMultiloader formatting error !!! LORA strength must be a float value.\nLine {0}: {1}'.format(index, line))
                                                    
                            return returnString

                        if (len(info[2]) == 0):
                            print('!!! TextLoraMultiloader formatting error !!! Missing loader.\nLine {0}: {1}'.format(index, line))
                            
                            return returnString
                        
                        match (info[2].strip()):
                            case "cgthree":
                                if "clip" not in input_types or input_types["clip"] == None:
                                    print('!!! TextLoraMultiloader error !!! CLIP input must be provided if using cgthree loader.\nLine {0}: {1}'.format(index, line))
                                                            
                                    return returnString
                                
                                try:
                                    float(info[3].strip())
                                except ValueError as e:
                                    print('!!! TextLoraMultiloader formatting error !!! CLIP strength must be a float value.\nLine {0}: {1}'.format(index, line))
                                                            
                                    return returnString
                            case "facok":
                                if (info[3].strip() not in block_types):
                                    print('!!! TextLoraMultiloader formatting error !!! Blocks must be "all", "single_blocks", or "double_blocks"\nLine {0}: {1}'.format(index, line))

                                    return returnString
                            case _:
                                print('!!! TextLoraMultiloader formatting error !!! Unrecognized loader.\nLine {0}: {1}'.format(index, line))
                                
                                return returnString
                    else:
                        print('!!! TextLoraMultiloader formatting error !!! Make sure each line is formatted as:\n\nLORA.safetensors | LORA_STRENGTH | cgthree | CLIP_STRENGTH\n\nor\n\nLORA.safetensors | LORA_STRENGTH | facok | BLOCKS.\n\nLine {0}: {1}'.format(index, line))
                              
                        return returnString
        
                index += 1

        return True
# routes = PromptServer.instance.routes

# @routes.post("/blackmagic/multiloader")
# async def multiloader_process_message(request):
#     print(request)

#     return web.json_response({"result": "done"})