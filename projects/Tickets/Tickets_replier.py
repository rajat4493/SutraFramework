# Tickets_replier.py
from sutra import Agent

replier = Agent(
    name='replier',
    objective='the agent will take the details about the ticket and the details from om classifer agent, it will create a highly professional and well articualted response to the original ticket will all details.Also ensure that you change tone based on the aggression of the initial ticket message to pacify the user',
    model='mistral:latest',
    prompt='''the agent will take the details about the ticket and the details from om classifer agent, it will create a highly professional and well articualted response to the original ticket will all details.Also ensure that you change tone based on the aggression of the initial ticket message to pacify the user

Input: {text}

Process the input and return structured JSON.
Be specific and clear in your output.

Return only valid JSON.''',
    expects_json=True,
    output_key='replier',
    required_keys=[],
    retries=1,
    temperature=0.1
)