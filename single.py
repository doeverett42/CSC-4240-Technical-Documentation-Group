#single-agent baseline: split numbered instructions by hand, then send each step to comfyui

import re
from datetime import datetime
from pathlib import Path

from comfyui import generate_image


def read_instructions():
    #read lines until the user enters an empty line, so pasted text can span several lines
    print("paste or type your numbered instructions. press enter on an empty line to finish.")
    print("type quit to leave.")
    lines = []
    while True:
        line = input("you: " if not lines else "").strip()
        if not lines and line.lower() in ("quit", "exit"):
            raise EOFError
        if not line:
            if lines:
                break
            continue
        lines.append(line)
    #join into one block of text; the splitter below does not care about line breaks
    return " ".join(lines)


def extract_steps(text):
    #find "1." first, then look for "2." after it, then "3." after that, and so on
    #(?<!\d) and (?!\d) stop numbers like "350.5" or "11." from counting as step markers
    markers = []
    number = 1
    position = 0
    while True:
        match = re.compile(rf"(?<!\d){number}\.(?!\d)").search(text, position)
        if not match:
            break
        markers.append(match)
        position = match.end()
        number += 1

    #each step runs from the end of its own marker to the start of the next marker
    steps = []
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        step = " ".join(text[marker.end():end].split())
        if step:
            steps.append(step)
    return steps


def main():
    while True:
        text = read_instructions()
        steps = extract_steps(text)
        if steps:
            break
        print("could not find a step starting with '1.'. please try again.")

    #show what was extracted before spending time on image generation
    print(f"found {len(steps)} steps:")
    for number, step in enumerate(steps, start=1):
        prompt = f"""
        Required action: {task.action}

        DO NOT: text, words, letters, numbers, captions, labels, annotations, logos, watermark, signatures, typography

        Instructions:
        - You are a conversational planner for technical guides covering physical tasks, software, interfaces, diagrams, and other procedures.
        - Distinguish a broad goal from complete instructions. Ask concise questions when essential information is missing.
        - Ask only what is needed to perform the task correctly. Do not ask for decorative preferences or information already supplied.
        - If clarification is needed, put your question in reply and return an empty tasks list. Do not return a partial plan.
        - Once you have enough information, consolidate the whole conversation into the final ordered tasks. Put a short summary in reply.
        - Make each visual step meaningfully different from the previous one through the actual procedure: changed shape, position, connection, surface, contents, arrangement, diagram, or interface state.
        - Avoid vague results such as ready, prepared, done, or complete on their own. Describe the concrete state those words represent.
        - Identify the target unambiguously using stable object or component names, relative positions, shapes, or control locations. Avoid ambiguous references such as the other one.
        - Do not invent measurements, ingredients, tools, temperatures, timings, or other procedural details. Ask if essential details are missing.
        - All generated images must be text-free. Do not request visible words, letters, numbers, labels, captions, annotations, logos, signatures, or watermarks, including on packaging or interfaces.
        - Prioritize the required change over repeating the previous arrangement. Preserve identities and unaffected details, while allowing the target's shape, color, position, contents, connections, or viewpoint to change when the action requires it.
        - Use consistent names for the same objects across steps.
        """
        print(f"{number}. {step}")

    #ask for the image server only after the steps are extracted
    server = input("comfyui address [http://127.0.0.1:8188]: ").strip()
    if not server:
        server = "http://127.0.0.1:8188"

    #keep each run's images together without replacing earlier runs
    output = Path(__file__).with_name("single-agent output") / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output.mkdir(parents=True)

    #queue the steps one at a time; each one waits for the previous image to finish
    for number, step in enumerate(steps, start=1):
        print(f"generating image {number}/{len(steps)}...", flush=True)
        generate_image(step, server, output / f"step_{number}.png")

    print(f"images saved to {output}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nstopped")
    except Exception as error:
        raise SystemExit(f"error: {error}")