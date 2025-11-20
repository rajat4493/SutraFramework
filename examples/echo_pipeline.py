# examples/echo_pipeline.py
# Minimal runnable example that does not require Ollama.
# Uses simple in-process mock agents that implement .run(dict)->dict

from sutra import Step, Pipeline

class MockAgent:
    def __init__(self, name, output_key):
        self.name = name
        self.output_key = output_key

    def run(self, inputs: dict) -> dict:
        text = inputs.get('text', '')
        if self.output_key == 'analyzer':
            # return a list of analysis items
            return {self.output_key: [
                {'summary': text[:140], 'category': 'Bug Report', 'root_cause': 'Crash on photo upload'}
            ]}
        if self.output_key == 'classifier':
            # return classification metadata
            return {self.output_key: [
                {'priority': 'High', 'team': 'mobile', 'ticket_type': 'bug'}
            ]}
        if self.output_key == 'replier':
            # return a reply object
            tone = 'calm'
            return {self.output_key: {
                'reply': f"Thanks for the report. We've identified the issue and our {('mobile' if 'mobile' in inputs.get('classifier',[{}])[0].get('team','') else 'engineering')} team is on it.",
                'tone': tone
            }}
        return {self.output_key: 'ok'}


def build():
    analyzer = MockAgent('analyzer', 'analyzer')
    classifier = MockAgent('classifier', 'classifier')
    replier = MockAgent('replier', 'replier')

    steps = [
        Step(analyzer, takes=['text']),
        Step(classifier, takes=['text', 'analyzer']),
        Step(replier, takes=['text', 'analyzer', 'classifier']),
    ]
    return Pipeline(steps)

DEFAULT_INPUT = {'text': 'Ticket #12847: App crashes on photo upload after update 2.3.1'}
