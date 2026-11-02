#chat with the reasoning agent, then send the finished tasks to comfyui

import asyncio
from datetime import datetime
from pathlib import Path

from agents import ChatReply, create_agent
from comfyui import generate_image, generate_next_image

from prompt_splitter import create_split, SplitResult

#[SINGLE AGENT - NO SPLIT, ONE AGENT DOES ALL STEPS]
async def run_single(long, server, output, num_steps): 
    output.mkdir(parents=True, exist_ok=True)
    step_paths = []
    previous_image = None

    print(f"single agent: generating {num_steps} images...", flush=True)

    for i in range(1, num_steps+1):
        destination = output / f"step_{i}.png"

        if i == 1:
            # first image = text only always
            await asyncio.to_thread(generate_image, long, server, destination)
        else:
            # second image = every image after will include text + prev image 
            await asyncio.to_thread(generate_next_image, long, previous_image, server, destination)

        previous_image = destination
        step_paths.append(destination)

    return step_paths

#WIP WIP WIP!!!!!!
#[MULTI AGENT - YES SPLIT, EACH AGENT FOCUSES ON A SINGULAR STEP]
async def run_multi(long, server, output):
    output.mkdir(parents=True, exist_ok=True)

    #split the long instruction into small instructions 
    splitter = create_split()
    print("multi prep: splitting instructions...", flush=True)
    result = await splitter.run(long, expected_output=SplitResult)
    tasks = result.output_structured.prompts

    #create a prompts file so we see what prompt is being fed to create each image
    prompts_file = output / "prompts.txt"
    prompts_file.write_text(
        "\n\n".join(f"Step {i}.) {p}" for i, p in enumerate(tasks, start=1)),
        encoding="utf-8"
    )


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
    
    #this is the entire re-interpreted plan from above that we'll feed to single/multi
    long_instruction = "\n".join(f"{t.action} -> {t.expected_state}" for t in tasks)

    #ask for the image server only after the conversation is complete
    server = input("comfyui address [http://127.0.0.1:8188]: ").strip()
    if not server:
        server = "http://127.0.0.1:8188"

    #keep each run's images together without replacing earlier runs
    output = Path(__file__).with_name("output") / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output.mkdir(parents=True)

    #run single agent  
    single = await run_single(long_instruction, server, output/"single", len(tasks))
    print(f"Single agent complete. Images saved to {output / 'single'}")


if __name__ == "__main__":
    #beeai uses async calls, so asyncio starts the main function
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print("\nstopped")
    except Exception as error:
        raise SystemExit(f"error: {error}")
