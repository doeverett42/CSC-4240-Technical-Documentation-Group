# chat with the reasoning agent, then send the finished tasks to ComfyUI

import asyncio
from datetime import datetime
from pathlib import Path

from agents import ChatReply, create_agent
from comfyui import generate_image, generate_next_image, upload_reference


async def generate_steps(tasks, server, output):
    # the chat agent has already split the plan into ordered tasks
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    previous_image = None
    prompts = []

    #comfyui requests run in worker threads while the chat loop uses asyncio
    for number, task in enumerate(tasks, start=1):
        # give the image model a specific change and the result it must show
        destination = output / f"step_{number}.png"
        prompt = f"Required change: {task.action}\nResult to show: {task.expected_state}"

        # keep the prompts beside the images so they are easy to inspect
        prompts.append(f"Step {number}\n{prompt}")
        (output / "prompts.txt").write_text("\n\n".join(prompts), encoding="utf-8")
        print(f"generating image {number}/{len(tasks)}...", flush=True)

        if previous_image is None:
            # the first image needs only text
            await asyncio.to_thread(generate_image, prompt, server, destination)
        else:
            # upload the last completed image and edit it using this step's prompt
            reference_image = await asyncio.to_thread(upload_reference, previous_image, server)
            await asyncio.to_thread(generate_next_image, prompt, reference_image, server, destination)

        # this result becomes the reference for the next step
        previous_image = destination


async def main():
    # create one agent so it remembers the whole conversation
    agent = create_agent()
    print("describe your task below. type quit to leave.")

    while True:
        # every message goes to the same reasoning agent
        message = input("you: ").strip()
        if message.lower() in ("quit", "exit"):
            return
        if not message:
            continue

        print("thinking...", flush=True)
        result = await agent.run(message, expected_output=ChatReply, max_iterations=5, total_max_retries=2)
        answer = ChatReply.model_validate(result.output_structured)
        print(f"agent: {answer.reply}", flush=True)

        # an empty task list means the agent still needs an answer
        # a finished task list moves the program on to image generation
        if answer.tasks:
            tasks = answer.tasks
            break

    # show the finished plan before generating images
    for number, task in enumerate(tasks, start=1):
        print(f"{number}. {task.action}")
        print(f"   expected: {task.expected_state}")

    # ask for the image server after the conversation is complete
    server = input("comfyui address [http://127.0.0.1:8188]: ").strip()
    if not server:
        server = "http://127.0.0.1:8188"

    # keep each run's images together without replacing earlier runs
    output = Path(__file__).with_name("output") / datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    # use the chat agent's task list directly to generate the guide
    await generate_steps(tasks, server, output)
    print(f"images saved to {output}")


if __name__ == "__main__":
    # BeeAI uses async calls, so asyncio starts the main function
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print("\nstopped")
    except Exception as error:
        raise SystemExit(f"error: {error}")
