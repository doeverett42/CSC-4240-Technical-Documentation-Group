# Instructions to Images

Describe a task, answer any questions from the planning agent, and generate an image for each step. The project uses Ollama for planning and ComfyUI for image generation.

## Setup

Install Python 3.11 or newer, Ollama, and a current version of ComfyUI.

From the project folder, run these commands:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
ollama pull deepseek-r1:14b
```

The planning agent uses the `deepseek-r1:14b` model in Ollama. The image workflow uses FLUX.2 Klein Base 9B with the Qwen3 8B text encoder.

Download these three files and place them in your ComfyUI model folders:

| Model file | ComfyUI folder |
| --- | --- |
| `flux-2-klein-base-9b-fp8.safetensors` | `models/diffusion_models/` |
| `qwen_3_8b_fp8mixed.safetensors` | `models/text_encoders/` |
| `full_encoder_small_decoder.safetensors` | `models/vae/` |

Use the models folder configured in your ComfyUI installation. Restart ComfyUI after adding the files. Their names must match the settings in `workflow_api.json`.

## Activate the Virtual Environment

For each used termanil run to get virutual environment:

```bash
source .venv/Scripts/activate
```

You should see `(.venv)` at the beginning of the prompt. To leave the environment, run `deactivate`.

## Run

**Start Ollama and ComfyUI locally before running this program.** Open ComfyUI Desktop and wait for its local server to be ready. Keep both services running while generating images; this program does not start them automatically.

In the same terminal, with the virtual environment active, run:

```bash
python main.py
```

1. Describe your task at the `you:` prompt.
2. Answer the agent's questions until it produces a plan.
3. At the ComfyUI address prompt, press Enter to use `http://127.0.0.1:8188`. If your local ComfyUI uses a different port, enter its address instead.
4. Wait for the images to be saved in a new folder under `output/`.

Type `quit` or `exit` during the conversation to leave. 

You can also enter the address of ComfyUI running on another computer. That computer must have the image models installed and accept connections from your computer.

## Project Files

- `main.py`: Runs the conversation and image generation.
- `agents.py`: Defines the planning agent and its model.
- `comfyui.py`: Sends requests to ComfyUI and downloads images.
- `workflow_api.json`: Contains the image settings used by this program.
- `flux2_klein_9b_learning_workflow.json`: Opens the workflow in the ComfyUI editor for manual testing.