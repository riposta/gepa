import dspy
import json
import uuid
from pathlib import Path


class GenerateEstimationExample(dspy.Signature):
    """Generate a realistic IT project estimation example."""

    context: str = dspy.InputField(desc="Project type and technologies to use")

    project_description: str = dspy.OutputField(desc="Realistic IT project requirements description")
    actual_hours: int = dspy.OutputField(desc="Actual number of man-hours (100-2000)")
    project_type: str = dspy.OutputField(desc="new | legacy | migration | ai")
    technologies: str = dspy.OutputField(desc="List of technologies as JSON array string")
    reasoning: str = dspy.OutputField(desc="Brief justification for the hours estimate")


CONTEXTS = [
    "new web project REST API Python",
    "legacy system migration Java 8 to Java 17",
    "SAP ERP system integration",
    "AI/ML pipeline project on telco data",
    "React Native mobile application",
    "self-service portal for telco customers",
    "microservices on Kubernetes AWS",
    "BI reporting system with Spark",
    "Oracle to PostgreSQL database modernization",
    "LLM customer service chatbot",
]


def generate(n: int, output_dir: str) -> int:
    generator = dspy.Predict(GenerateEstimationExample)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for i in range(n):
        context = CONTEXTS[i % len(CONTEXTS)]
        result = generator(context=context)
        example = {
            "project_description": result.project_description,
            "actual_hours": result.actual_hours,
            "project_type": result.project_type,
            "technologies": result.technologies,
            "reasoning": result.reasoning,
            "source": "synthetic",
        }
        fname = out / f"synthetic_{uuid.uuid4().hex[:8]}.json"
        fname.write_text(json.dumps(example, ensure_ascii=False, indent=2))

    return n


if __name__ == "__main__":
    import sys
    from gepa.config.settings import settings
    lm = dspy.LM(
        model=settings.llm_model,
        api_key=settings.llm_api_key.get_secret_value() or None,
    )
    dspy.configure(lm=lm)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    count = generate(n=n, output_dir="gepa/data/training")
    print(f"Generated {count} synthetic examples.")
