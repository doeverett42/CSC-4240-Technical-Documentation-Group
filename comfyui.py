"""send tasks to ComfyUI and download the generated images."""

import json
import mimetypes
import time
from pathlib import Path, PurePosixPath

import requests


def generate_image(task, server, destination):
    # load the text-only workflow for the first image
    workflow_file = Path(__file__).with_name("workflow_api.json")
    workflow = json.loads(workflow_file.read_text(encoding="utf-8"))

    # node 74 holds the positive prompt
    workflow["74"]["inputs"]["text"] = "Simple instructional illustration on a plain background. " + task
    send_workflow(workflow, server, destination)

#upload a local image and return its filename on the comfyui server
def upload_reference(image, server):
    image = Path(image)
    mime_type = mimetypes.guess_type(image.name)[0] or "application/octet-stream"

    # send the image itself; a local filename is not enough for a remote server
    with image.open("rb") as image_file:
        response = requests.post(
            server.rstrip("/") + "/upload/image",
            files={"image": (image.name, image_file, mime_type)},
            data={
                "type": "input",
                "subfolder": "instructions/references",
                "overwrite": "false"
            },
            timeout=60
        )
    response.raise_for_status()
    uploaded = response.json()

    # ComfyUI may rename the upload; use its returned name and forward slashes
    return str(PurePosixPath(uploaded.get("subfolder", "")) / uploaded["name"])


def generate_next_image(task, reference_image, server, destination):
    # load the image-and-text workflow for every step after the first
    workflow_file = Path(__file__).with_name("workflow_edit_api.json")
    workflow = json.loads(workflow_file.read_text(encoding="utf-8"))

    # node 80 loads the uploaded previous image using its server filename
    workflow["80"]["inputs"]["image"] = reference_image

    # node 74 describes what should change and what should stay consistent
    workflow["74"]["inputs"]["text"] = (
        "Edit the reference image into the requested instructional state. "
        "Preserve the same objects, materials, colors, illustration style, lighting, "
        "background, and camera viewpoint wherever the requested action allows. "
        "Change the object's shape, arrangement, or contents as required. "
        "Show one resulting scene, without extra panels or labels.\n" + task
    )
    send_workflow(workflow, server, destination)

#queue either workflow, wait for its result, and save the image
def send_workflow(workflow, server, destination):
    server = server.rstrip("/")
    destination = Path(destination)

    # node 75 saves the image on the ComfyUI server
    workflow["75"]["inputs"]["filename_prefix"] = "instructions/" + destination.stem
    response = requests.post(server + "/prompt", json={"prompt": workflow}, timeout=30)
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        # include node errors so missing models or nodes are easy to identify
        raise RuntimeError(f"ComfyUI rejected the workflow: {response.text}") from error
    prompt_id = response.json()["prompt_id"]

    # keep the job ID and settings beside the image, even if the job times out
    destination.parent.mkdir(parents=True, exist_ok=True)
    record = {"prompt_id": prompt_id, "prompt": workflow}
    destination.with_suffix(".json").write_text(json.dumps(record, indent=2), encoding="utf-8")

    # check the job history once a second, allowing up to 15 minutes
    deadline = time.monotonic() + 900
    while time.monotonic() < deadline:
        response = requests.get(server + "/history/" + prompt_id, timeout=30)
        response.raise_for_status()
        job = response.json().get(prompt_id, {})

        # stop if ComfyUI reports an error instead of waiting for an image
        if job.get("status", {}).get("status_str") == "error":
            raise RuntimeError(f"ComfyUI failed: {job['status'].get('messages')}")

        # node 75's history entry tells us where the completed image was saved
        images = job.get("outputs", {}).get("75", {}).get("images", [])
        if images:
            response = requests.get(server + "/view", params=images[0], timeout=60)
            response.raise_for_status()

            # copy the finished image from the server into this run's folder
            destination.write_bytes(response.content)
            return

        time.sleep(1)

    # a client timeout does not cancel the job on the ComfyUI server
    raise TimeoutError(f"ComfyUI job {prompt_id} took too long; it may still be running")