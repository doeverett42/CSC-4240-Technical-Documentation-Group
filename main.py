#chat with the reasoning agent, then send the finished tasks to comfyui

import asyncio
from datetime import datetime
from pathlib import Path

from agents import ChatReply, create_agent
from comfyui import generate_image


async def main():
    #create this once, outside the loop, so the conversation is remembered
    agent = create_agent()
    print("describe your task below. type quit to leave.")

    while True:
        #every message goes to the same reasoning agent
        message = input("you: ").strip()
        if message.lower() in ("quit", "exit"):
            return
        if not message:
            continue

        print("thinking...", flush=True)
        result = await agent.run(
            message, expected_output=ChatReply, max_iterations=5, total_max_retries=2
        )
        answer = ChatReply.model_validate(result.output_structured)
        print(f"agent: {answer.reply}", flush=True)

        #no tasks means the reply is a question; loop back for the user's answer
        #a finished task list ends the chat and moves on to image generation
        if answer.tasks:
            tasks = answer.tasks
            break

    #show the consolidated plan before sending it to the image worker
    for number, task in enumerate(tasks, start=1):
        print(f"{number}. {task.action}")
        print(f"   expected: {task.expected_state}")

    #ask for the image server only after the conversation is complete
    server = input("comfyui address [http://127.0.0.1:8188]: ").strip()
    if not server:
        server = "http://127.0.0.1:8188"

    #keep each run's images together without replacing earlier runs
    output = Path(__file__).with_name("output") / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output.mkdir(parents=True)

    #send each action with its expected result so the image has enough context
    for number, task in enumerate(tasks, start=1):
        print(f"generating image {number}/{len(tasks)}...", flush=True)
        prompt = f"action: {task.action}\nexpected result: {task.expected_state}"
        generate_image(prompt, server, output / f"step_{number}.png")

    print(f"images saved to {output}")


if __name__ == "__main__":
    #beeai uses async calls, so asyncio starts the main function
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print("\nstopped")
    except Exception as error:
        raise SystemExit(f"error: {error}")
