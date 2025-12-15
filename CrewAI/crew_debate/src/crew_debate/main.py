#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from crew_debate.crew import CrewDebate

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'motion': 'There need to be strict regulations on AI development.'
    }

    try:
        results = CrewDebate().crew().kickoff(inputs=inputs)
        print(results.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")