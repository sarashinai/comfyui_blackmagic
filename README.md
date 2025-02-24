# Black Magic Nodes

A collection of ComfyUI nodes I created to solve specific issues I was having.

## Installation

1. Install [ComfyUI](https://docs.comfy.org/get_started).

### Install with ComfyUI-Manager

2. Install [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)
3. Look up this extension in ComfyUI-Manager. You can find it by searching for `black magic` or `sarashinai`.

### Install manually with git

2. From a command line, change directory to `ComfyUI/custom_nodes`
3. Run `git clone https://github.com/sarashinai/comfyui_blackmagic.git`

### Run and test
4. Restart ComfyUI.

## Nodes

### TextLoraMultiloader
There are a number of custom nodes that load multiple LORA to keep the workflow tidy. When I started generating 
Hunyuan video, and needed to choose which blocks to use, the multiloaders didn't provide the option. I also like
to store/copy configurations easily from one workflow to another, so I create a LORA loader that uses multiline
text instructions to load LORA. Currently, it uses loading code from [cgthree's Power Loader](https://github.com/rgthree/rgthree-comfy) 
and [facok's HunyuanVideoMultiLora](https://github.com/facok/ComfyUI-HunyuanVideoMultiLora). You can see these
represented in the names of the loaders used by TextLoraMultiloader. Only the multiline field is used when
running the workflow, the widgets beneath are for adding and updating the text. This loader will ignore any blank
line and any line that starts with a `#` symbol.

![image](https://github.com/user-attachments/assets/3ea6f19b-a4e3-4b16-9da2-f6f218ac7c2f)


### TextFormatter
The way that ComfyUI offers [file name formatting](https://comfyuidoc.com/Interface/SaveFileFormatting.html) is 
very useful for avoiding file name collisions and organization but not every node implements it. When I used a node
that didn't, the presence of the `%` sign in the actual file name caused problems for FFMPEG and files weren't
outputted correctly, losing generation time. This node takes the template text you enter and runs it through
the ComfyUI formatting system in real-time so you can see the result before running the workflow and then you 
can have it send the result out to a file name prefix input, though I imagine there are other uses I haven't
thought of.

![image](https://github.com/user-attachments/assets/06545c4b-af4e-4782-ba05-a9c29cb7c4b0)

## Publish to Github

Install Github Desktop or follow these [instructions](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) for ssh.

1. Create a Github repository that matches the directory name. 
2. Push the files to Git
```
git add .
git commit -m "project scaffolding"
git push
``` 


## Publishing to Registry

If you wish to share this custom node with others in the community, you can publish it to the registry. We've already auto-populated some fields in `pyproject.toml` under `tool.comfy`, but please double-check that they are correct.

You need to make an account on https://registry.comfy.org and create an API key token.

- [ ] Go to the [registry](https://registry.comfy.org). Login and create a publisher id (everything after the `@` sign on your registry profile). 
- [ ] Add the publisher id into the pyproject.toml file.
- [ ] Create an api key on the Registry for publishing from Github. [Instructions](https://docs.comfy.org/registry/publishing#create-an-api-key-for-publishing).
- [ ] Add it to your Github Repository Secrets as `REGISTRY_ACCESS_TOKEN`.

A Github action will run on every git push. You can also run the Github action manually. Full instructions [here](https://docs.comfy.org/registry/publishing). Join our [discord](https://discord.com/invite/comfyorg) if you have any questions!

