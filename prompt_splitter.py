from pydantic import BaseModel 
from beeai_framework.agents.requirement import RequirementAgent
from agents import model 

class SplitResult(BaseModel):
    #the split should result in a list of smaller prompts 
    prompts: list[str]

def create_split():
    #tells agent to split the long prompt into smaller prompts while attempting to preserve order
    return RequirementAgent(
        llm = model,
        instructions = [
            "You are an instruction splitter. Take the complete technical instructions and break them down into minimal independent steps.",
            "Each step should be a short, self-contained prompt suitable for image generation. ",
            "DO NOT merge steps that produce different visual states - preserve order and prior dependencies. ",
            "Return only the list of prompts in the required schema."
        ],

    )