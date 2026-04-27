import dspy
from gepa.dspy_modules.signatures import WycenaIT


def create_estimator() -> dspy.ChainOfThought:
    return dspy.ChainOfThought(WycenaIT)
