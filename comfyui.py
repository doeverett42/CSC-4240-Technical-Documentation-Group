"""send a task to a remote comfyui server and download the finished image."""

import json
import time
from pathlib import Path

import requests


def generate_image(task, server, destination):
    # load the supplied workflow in the format comfyui's api accepts
    workflow_file = Path(__file__).with_name("workflow_api.json")
    workflow = json.loads(workflow_file.read_text(encoding="utf-8"))

    # node 74 holds the positive prompt; the task goes straight into it
    workflow["74"]["inputs"]["text"] = "Simple instructional illustration on a plain background. " + task
    workflow["75"]["inputs"]["filename_prefix"] = "instructions/" + destination.stem

    # /prompt queues the workflow on the remote computer
    # comfyui runs the image model there, not in this python program
    server = server.rstrip("/")
    response = requests.post(server + "/prompt", json={"prompt": workflow}, timeout=30)
    response.raise_for_status()
    prompt_id = response.json()["prompt_id"]

    # check the job's history once a second, allowing up to 15 minutes
    deadline = time.monotonic() + 900
    while time.monotonic() < deadline:
        response = requests.get(server + "/history/" + prompt_id, timeout=30)
        response.raise_for_status()
        job = response.json().get(prompt_id, {})

        # stop if comfyui reports a failure instead of waiting for an image
        if job.get("status", {}).get("status_str") == "error":
            raise RuntimeError(f"comfyui failed: {job['status'].get('messages')}")

        # node 75 saves the image; its history entry tells us where to find it
        images = job.get("outputs", {}).get("75", {}).get("images", [])
        if images:
            image = images[0]
            response = requests.get(server + "/view", params=image, timeout=60)
            response.raise_for_status()

            # copy the image from the remote server into this run's output folder
            destination.write_bytes(response.content)
            return

        time.sleep(1)

    raise TimeoutError("comfyui took too long; the remote job may still be running")
