# Tickets_analyzer.py
from sutra import Agent

analyzer = Agent(
    name='analyzer',
    objective='the agent will take ticket details as input and analyze the ticket to find the details which are useful to traige the ticket',
    model='mistral:latest',
    prompt='''the agent will take ticket details as input and analyze the ticket to find the details which are useful to traige the ticket

Input: {text}

Process the input and return structured JSON.
Be specific and clear in your output.

Return only valid JSON.''',
    expects_json=True,
    output_key='analyzer',
    required_keys=[],
    retries=1,
    temperature=0.1
)