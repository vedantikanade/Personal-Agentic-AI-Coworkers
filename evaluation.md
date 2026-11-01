# Evaluation Plan

## Agent 1 metrics

- **Relevance:** at least two of three selected articles should match the learner's interests or growth areas.
- **Source quality:** every article should have a source, date, and URL.
- **Summary faithfulness:** compare generated summaries with the source and manually verify key claims.
- **Time fit:** the brief should fit the learner's 15-minute daily limit.
- **Personalization:** compare recommendations for two different profiles and verify that rankings change.

## Agent 2 metrics

- **Technical coverage:** questions should cover coding, data quality, ML, healthcare AI, and RAG.
- **Feedback usefulness:** each answer receives a score, explanation, and next action.
- **Consistency:** the same answer should receive a similar score across repeated runs.
- **Progress:** compare scores and identified gaps across coaching sessions.
- **Career relevance:** activities should map to skills requested in healthcare AI or data science internship descriptions.

## Prototype test cases

1. Run Agent 1 with the default profile and confirm exactly three recommendations.
2. Change the profile to cybersecurity and confirm the ranking logic responds to different topics.
3. Give Agent 2 a detailed technical answer and verify relevant keywords are recognized.
4. Give Agent 2 a blank or vague answer and verify that it reports a gap and recommends practice.
5. Confirm every recommendation includes a URL and source metadata.
