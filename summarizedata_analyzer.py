# summarizedata_analyzer.py
from sutra import Agent

analyzer = Agent(
    name='analyzer',
    objective='Analyze and understand the input content',
    model='llama3:latest',
    prompt='''Analyze the following content thoroughly.

Content: {text}

Break down and analyze this content. Return JSON with:
- "content_type": what type of content this is
- "key_themes": main themes or topics found
- "complexity": how complex the content is (simple/medium/complex)
- "analysis": detailed analysis of the content
- "notable_elements": any important elements worth highlighting

Return only valid JSON.''',
    expects_json=True,
    output_key='analyzer',
    required_keys=['content_type', 'key_themes', 'analysis'],
    retries=1,
    temperature=0.1
)