#!/usr/bin/env python
import warnings

from datetime import datetime

from stock_picker.crew import StockPicker

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    inputs = {
        'sector': 'Technology',
        'current_year': str(datetime.now().year)
    }

    result = StockPicker().crew().kickoff(inputs=inputs)
    print("\n\n=== FINAL DECISION ===\n\n")
    print(result.raw)


if __name__ == '__main__':
    run()