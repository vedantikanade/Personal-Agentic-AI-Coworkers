# Personal Agentic AI Coworkers

This project contains two personalized AI coworker prototypes for healthcare AI and data science:

1. **DailyTechUpgradeAgent** - recommends three technical readings and produces a 15-minute learning brief.
2. **nextLevelPersonalCoachForCareerLevel** - evaluates internship readiness through questions, feedback, and a targeted improvement plan.

## Personalization profile

- Primary focus: healthcare data quality, data science, AI/ML, RAG, and AI evaluation.
- Career goal: prepare for a healthcare AI or data science internship.
- Current experience: RAG assignments and the CRISP-DM process.
- Main improvement area: coding and practical implementation.
- Daily learning time: 15 minutes.

## Run the prototype

```bash
python3 app.py
```

For the browser interface, install the UI dependency once and launch:

```bash
python3 -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

The prototype first attempts live retrieval from public RSS feeds and a public web search endpoint. If live retrieval is unavailable, it safely falls back to the local curated catalog so the demonstration still runs. No API key is required for the baseline.

## Files

- `app.py`: command-line demo and menu for both agents.
- `streamlit_app.py`: browser UI with tabs for learning, coaching, and progress.
- `agent1_daily_tech_upgrade.py`: article ranking, summarization, personalization, and learning-brief logic.
- `agent2_career_coach.py`: competency model, interview questions, answer evaluation, scoring, and action plan.
- `live_retrieval.py`: live RSS article retrieval and public opportunity-search connector.
- `user_profile.json`: editable learner profile and career target.
- `memory_store.py` and `memory.json`: persistent article and coaching history.
- `articles.json`: fallback article catalog used when live retrieval is unavailable.
- `architecture.md`: workflow, tools, data sources, memory, and Mermaid diagrams.
- `sample_results.md`: example outputs for the assignment submission.
- `evaluation.md`: evaluation criteria and measurable success indicators.
- `requirements.txt`: intentionally empty; the prototype uses Python's standard library.

## Prototype limitations and next iteration

The prototype uses live public retrieval where available. A production version would add source-date validation, citation checks, LLM summarization, structured job-board APIs, and a persistent database for long-term progress history.
