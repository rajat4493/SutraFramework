# Tickets_classifier.py
from sutra import Agent

classifier = Agent(
    name='classifier',
    objective='agent will take the input from analyzer agent and then classify the ticket in category,priority, team it should be assigned to, etc.',
    model='mistral:latest',
    prompt='''agent will take the input from analyzer agent and then classify the ticket in category,priority, team it should be assigned to, etc.

Input: {text}

Process the input and return structured JSON.
Be specific and clear in your output.

Return only valid JSON.''',
    expects_json=True,
    output_key='classifier',
    required_keys=[],
    retries=1,
    temperature=0.1
)