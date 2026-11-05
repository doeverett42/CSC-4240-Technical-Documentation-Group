# Instructions to Images

Describe a task, answer any questions from the chat agent, and generate an image for each step. The same agent creates the ordered task list. Ollama runs the agent, and ComfyUI generates the images.

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

Use the models folder configured in your ComfyUI installation. Restart ComfyUI after adding the files. Their names must match the settings in both `workflow_api.json` and `workflow_edit_api.json`. Both workflows use the same models and built-in ComfyUI nodes.

## Activate the Virtual Environment

In each new Git Bash terminal, open the project folder and activate the virtual environment:

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
4. Wait for the images to be saved under `output/<run time>/`.

Type `quit` or `exit` during the conversation to leave.

You can also enter the address of ComfyUI running on another computer. That computer must have the image models installed and accept connections from your computer.

## Consistent Images

The program uses the chat agent's task list directly:

1. Generate the first image from text using `workflow_api.json`.
2. Upload the completed image and use it with the next task's text in `workflow_edit_api.json`.
3. Repeat with each newly generated image: image 2 uses image 1, image 3 uses image 2, and so on.

Each prompt describes only the current action and expected result. The previous image carries the visual state forward and helps preserve the objects, colors, viewpoint, and illustration style, though details may still vary.

Each run saves the images, `prompts.txt`, and a JSON file beside each image containing its workflow settings and ComfyUI job ID.

## Project Files

- `main.py`: Chats with the user, then generates an image for each task.
- `agents.py`: Defines the single chat agent, its model, and the task format.
- `comfyui.py`: Uploads the previous image, submits workflows, and downloads images.
- `workflow_api.json`: Contains the image settings used by this program.
- `workflow_edit_api.json`: Takes a reference image and text to generate later steps.
- `flux2_klein_9b_learning_workflow.json`: Opens the workflow in the ComfyUI editor for manual testing.
- `flux2_klein_9b_edit_workflow.json`: Opens the image-editing workflow in ComfyUI for manual testing.