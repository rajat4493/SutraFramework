# catagent_classifier.py
from sutra import Agent

classifier = Agent(
    name='classifier',
    objective='Classify and categorize content appropriately',
    model='llama3:latest',
    prompt='''Classify the following content into appropriate categories.

Content to classify: {text}
Analysis (if available): {analyzer}

Classify this content. Return JSON with:
- "primary_category": main category (e.g., business, technical, personal)
- "subcategory": more specific classification
- "priority_level": importance level (low/medium/high)
- "tags": list of relevant tags
- "confidence": confidence in classification (1-10)
- "reasoning": brief explanation of classification choice

Return only valid JSON.''',
    expects_json=True,
    output_key='classifier',
    required_keys=['primary_category', 'confidence', 'reasoning'],
    retries=1,
    temperature=0.1
)