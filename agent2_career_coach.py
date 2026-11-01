"""nextLevelPersonalCoachForCareerLevel: interactive readiness prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from live_retrieval import search_opportunities
from memory_store import record_coaching_session


BASE_DIR = Path(__file__).parent

COMPETENCIES = {
    "coding": "Python implementation and ability to explain code choices",
    "data_quality": "data cleaning, missing values, leakage, and validation",
    "machine_learning": "model selection, metrics, overfitting, and generalization",
    "healthcare_ai": "clinical context, bias, privacy, safety, and responsible evaluation",
    "rag": "retrieval, grounding, citations, and RAG evaluation",
}

QUESTIONS = [
    {"competency": "coding", "question": "How would you load a healthcare CSV, inspect missing values, and report the percentage missing in each column?"},
    {"competency": "data_quality", "question": "A model has 95% accuracy on a healthcare dataset. What checks would you perform before trusting that result?"},
    {"competency": "machine_learning", "question": "Explain overfitting and name two ways to reduce it."},
    {"competency": "healthcare_ai", "question": "What risks should be evaluated before deploying an AI model that supports a clinical decision?"},
    {"competency": "rag", "question": "How would you evaluate whether a healthcare RAG system produces grounded answers?"},
]


def discover_opportunities(profile: dict[str, Any]) -> list[dict[str, str]]:
    query = "healthcare AI data science internship Python machine learning"
    live_results = search_opportunities(query)
    if live_results:
        return live_results
    with open(BASE_DIR / "opportunities.json", encoding="utf-8") as handle:
        return json.load(handle)


def extract_required_skills(text: str) -> list[str]:
    vocabulary = [
        "python", "sql", "pandas", "machine learning", "deep learning", "statistics",
        "data visualization", "tensorflow", "pytorch", "scikit-learn", "rag", "llm",
        "healthcare", "data cleaning", "cloud", "communication",
    ]
    lowered = text.lower()
    return [skill for skill in vocabulary if skill in lowered]


def load_profile() -> dict[str, Any]:
    with open(BASE_DIR / "user_profile.json", encoding="utf-8") as handle:
        return json.load(handle)


def evaluate_answer(question: dict[str, str], answer: str) -> dict[str, Any]:
    answer_lower = answer.lower()
    competency = question["competency"]
    keyword_groups = {
        "coding": ["pandas", "read_csv", "missing", "isna", "percent"],
        "data_quality": ["leakage", "imbalance", "validation", "bias", "distribution"],
        "machine_learning": ["overfit", "cross-validation", "regularization", "test", "generaliz"],
        "healthcare_ai": ["bias", "privacy", "safety", "clinical", "fairness", "explain"],
        "rag": ["retrieval", "ground", "citation", "faithful", "precision", "recall"],
    }
    matched = [word for word in keyword_groups[competency] if word in answer_lower]
    score = min(5, max(1, len(matched)))
    feedback = (
        "Strong start: your response mentioned relevant evaluation ideas. Add a concrete method or metric."
        if score >= 3
        else "Needs development: define the concept, give a practical example, and name a metric or validation step."
    )
    return {"competency": competency, "score": score, "matched_terms": matched, "feedback": feedback}


def readiness_report(answers: dict[int, str]) -> dict[str, Any]:
    evaluations = [evaluate_answer(question, answers.get(index, "")) for index, question in enumerate(QUESTIONS)]
    overall = round(sum(item["score"] for item in evaluations) / len(evaluations), 1)
    gaps = [item["competency"] for item in evaluations if item["score"] <= 2]
    strengths = [item["competency"] for item in evaluations if item["score"] >= 3]
    plan = [
        "Complete one Python/pandas data-cleaning exercise using a small healthcare dataset.",
        "Practice explaining accuracy, precision, recall, calibration, and subgroup performance.",
        "Build a tiny RAG demo with citations and test it with five grounded questions.",
        "Review privacy, bias, safety, and human-in-the-loop considerations for healthcare AI.",
    ]
    return {"overall_score_out_of_5": overall, "strengths": strengths, "knowledge_gaps": gaps, "evaluations": evaluations, "action_plan": plan}


def interactive_session() -> None:
    profile = load_profile()
    print(f"\nTarget: {profile['career_goal']}")
    print("Paste a job description, or press Enter to use the default healthcare AI internship target.")
    job_text = input("Job description: ").strip()
    if job_text:
        required = extract_required_skills(job_text)
        print(f"Detected skills: {', '.join(required) or 'No recognized skills; continue with core assessment.'}")
    else:
        opportunities = discover_opportunities(profile)
        print(f"Live opportunity search returned {len(opportunities)} result(s).")
        for item in opportunities[:3]:
            print(f"- {item['title']}: {item['url']}")
    print("\nCareer readiness session: answer each question in 1-3 sentences.\n")
    answers: dict[int, str] = {}
    for index, question in enumerate(QUESTIONS):
        print(f"{index + 1}. ({question['competency']}) {question['question']}")
        answers[index] = input("Your answer: ").strip()
        print()
    report = readiness_report(answers)
    record_coaching_session(report)
    print("CAREER READINESS REPORT")
    print(f"Overall score: {report['overall_score_out_of_5']}/5")
    print(f"Strengths: {', '.join(report['strengths']) or 'Not demonstrated yet'}")
    print(f"Knowledge gaps: {', '.join(report['knowledge_gaps']) or 'Continue practicing for deeper mastery'}")
    for item in report["evaluations"]:
        print(f"\n{item['competency']}: {item['score']}/5 - {item['feedback']}")
    print("\nRecommended improvement plan:")
    for item in report["action_plan"]:
        print(f"- {item}")


if __name__ == "__main__":
    interactive_session()
