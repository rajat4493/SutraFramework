# summarizedata_pipeline.py
# Pipeline: Summarize the text and classify it
# Edit AGENT_ORDER list to choose which agents to use and in what order

from sutra import Step, Pipeline
import importlib

# Configure your pipeline by listing agent file names in execution order
# Examples:
# AGENT_ORDER = ["summarizedata_classifier"]  # Classification only
# AGENT_ORDER = ["summarizedata_summarizer"]  # Summary only
# AGENT_ORDER = ["summarizedata_analyzer", "summarizedata_classifier"]  # Analysis + Classification
AGENT_ORDER = ["summarizedata_analyzer", "summarizedata_classifier", "summarizedata_summarizer"]  # Full workflow

def build():
    steps = []
    previous_outputs = ['text']  # Start with input text
    
    for agent_file in AGENT_ORDER:
        # Import the agent from its file
        module = importlib.import_module(agent_file)
        agent_name = agent_file.split('_')[-1]  # Get agent name from filename
        agent = getattr(module, agent_name)
        
        # Create step with outputs from all previous agents
        steps.append(Step(agent, takes=previous_outputs.copy()))
        
        # Add this agent's output for next agent
        previous_outputs.append(agent_name)
    
    return Pipeline(steps)

DEFAULT_INPUT = {'text': 'Sample text to process - replace with your actual content'}