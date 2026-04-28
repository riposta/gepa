import dspy
from gepa.dspy_modules.signatures import ITEstimation


def create_estimator() -> dspy.ChainOfThought:
    return dspy.ChainOfThought(ITEstimation)
