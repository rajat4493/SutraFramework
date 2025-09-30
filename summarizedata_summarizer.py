# summarizedata_summarizer.py
from sutra import Agent

summarizer = Agent(
    name='summarizer',
    objective='Create clear summary and actionable output',
    model='llama3:latest',
    prompt='''Create a comprehensive summary and final output.

Original content: {text}
Analysis: {analyzer}
Classification: {classifier}

Create final summary. Return JSON with:
- "summary": clear 2-3 sentence summary
- "key_points": list of most important points
- "action_items": suggested next steps or actions
- "final_assessment": overall assessment of the content
- "recommendations": any recommendations based on the content

Return only valid JSON.''',
    expects_json=True,
    output_key='summarizer',
    required_keys=['summary', 'key_points', 'final_assessment'],
    retries=1,
    temperature=0.1
)