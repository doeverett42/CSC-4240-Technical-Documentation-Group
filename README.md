# Instructions to Images

Generate an image for each step of a technical procedure with ComfyUI.

## Setup

Install Python 3.12 and ComfyUI with FLUX.2 support. From the project folder on Windows, run the following.

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Place these files in the corresponding ComfyUI model directories, then start ComfyUI.

| Model file | ComfyUI directory |
| --- | --- |
| `flux-2-klein-base-9b-fp8.safetensors` | `models/diffusion_models/` |
| `qwen_3_8b_fp8mixed.safetensors` | `models/text_encoders/` |
| `full_encoder_small_decoder.safetensors` | `models/vae/` |

For multi-agent mode, also install and start Ollama, install BeeAI, and pull the planning model.

```powershell
./.venv/Scripts/python.exe -m pip install beeai-framework==0.1.80
ollama pull deepseek-r1:14b
```

## Run

When prompted for the ComfyUI address, press Enter to use `http://127.0.0.1:8188` or enter your server URL. Both modes save a PNG and a matching workflow JSON file for each step.

### Multi-agent mode

```powershell
./.venv/Scripts/python.exe main.py
```

Describe your task and answer any follow-up questions. The Ollama agent creates an ordered plan. ComfyUI generates the first image from text and uses the previous image as a reference for each later step.

Each run saves to `multi-agent output/<timestamp>/` and includes `prompts.txt`.

### Single-agent mode

```powershell
./.venv/Scripts/python.exe single.py
```

Paste or type instructions numbered `1.`, `2.`, `3.` and press Enter on a blank line when finished. ComfyUI generates each image independently from its step.

Each run saves to `single-agent output/<timestamp>/`.
