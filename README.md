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

Each prompt names the required change and describes the concrete result to show. The agent identifies the target and its new state, rather than using vague results such as "ready" or "done." This applies to physical tasks, diagrams, software, and interface instructions.

Later images edit the previous result. The requested change takes priority over keeping the old arrangement; unaffected details and visual style remain consistent. Steps with no visible change retain their real instructions without inventing visual evidence of completion. Generated details may still vary.

Images are instructed to contain no text, letters, numbers, labels, captions, logos, or watermarks, including on packaging and interfaces. Edits also remove existing writing from the reference image. Written procedure details stay in the instructions rather than appearing inside the images.

The base drawing and editing instructions are stored in node `74` of the two API workflow files. `comfyui.py` puts the current step before those general instructions. You can tune the wording in the workflow files without changing the Python code.

Both API workflows and the edit canvas use Euler, 20 steps, and CFG 7. The first image uses seed 42; each later image-editing call gets a new random seed. The edit canvas also randomizes its seed between queued edits. The Python app saves the actual seed in the JSON file beside each image.

Each run saves the images, `prompts.txt`, and a JSON file beside each image containing its workflow settings and ComfyUI job ID.

## Manual Testing in ComfyUI

Open `flux2_klein_9b_edit_workflow.json` in ComfyUI and choose a source in **Reference image**. At the top of **Edit instruction / target state**, add your required change and the result to show. Keep the general no-text instructions underneath, then queue the workflow.

To continue, use the new image as the reference for the next step. The canvas mirrors `workflow_edit_api.json`; if you change its settings manually, update the API file too for the Python app to use them.

## Project Files

- `main.py`: Chats with the user, then generates an image for each task.
- `agents.py`: Defines the single chat agent, its model, and the task format.
- `comfyui.py`: Uploads the previous image, submits workflows, and downloads images.
- `workflow_api.json`: Generates the first image from text.
- `workflow_edit_api.json`: Takes a reference image and text to generate later steps.
- `flux2_klein_9b_edit_workflow.json`: The same editing workflow in ComfyUI canvas format for manual testing.
