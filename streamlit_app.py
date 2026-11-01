"""Browser UI for the two personalized AI coworkers."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from agent1_daily_tech_upgrade import build_learning_brief, load_json, normalize_live_article, rank_articles
from agent2_career_coach import QUESTIONS, discover_opportunities, extract_required_skills, readiness_report
from live_retrieval import fetch_live_articles
from memory_store import load_memory, record_article_brief, record_coaching_session

BASE_DIR = Path(__file__).parent

def load_profile() -> dict:
    with open(BASE_DIR / "user_profile.json", encoding="utf-8") as handle:
        return json.load(handle)

def save_profile(profile: dict) -> None:
    with open(BASE_DIR / "user_profile.json", "w", encoding="utf-8") as handle:
        json.dump(profile, handle, indent=2)

st.set_page_config(page_title="Healthcare AI Coworkers", page_icon="🧠", layout="wide")
st.title("🧠 Personal Agentic AI Coworkers")
st.caption("A personalized learning and career-readiness workspace for healthcare AI and data science.")
profile = load_profile()

with st.sidebar:
    st.header("Learner profile")
    st.write(f"**Goal:** {profile['career_goal']}")
    st.write(f"**Daily learning:** {profile['daily_minutes']} minutes")
    st.write("**Interests:** " + ", ".join(profile["interests"]))
    if st.button("Refresh live sources"):
        st.rerun()

tab1, tab2, tab3 = st.tabs(["📚 Daily Technical Upgrade", "🎯 Career Coach", "📈 Progress & Profile"])

with tab1:
    st.header("DailyTechUpgradeAgent")
    st.write("Find three relevant technical readings and fit them into a 15-minute session.")
    if st.button("Generate today's brief", type="primary"):
        with st.spinner("Checking live technical sources and ranking articles for your profile..."):
            live = [normalize_live_article(item) for item in fetch_live_articles()]
            fallback = load_json("articles.json")
            articles = rank_articles(live + fallback, profile)
            if len(articles) < 3:
                chosen = {item.get("url") for item in articles}
                articles.extend(item for item in fallback if item.get("url") not in chosen)
            articles = articles[:3]
            record_article_brief(articles)
        st.success("Learning brief generated and saved to memory.")
        st.caption("15 minutes: 8-minute deep dive + two 3-minute scans + one-minute reflection")
        for index, article in enumerate(articles, start=1):
            role = "Deep dive" if index == 1 else "Quick scan"
            summary = article.get("short_summary") or article.get("summary", "")
            if not article.get("short_summary") and len(summary) > 220:
                summary = summary[:217].rsplit(" ", 1)[0] + "..."
            st.markdown(f"**{index}. {role}: {article['title']}**")
            st.caption(f"{article['source']} · {article['date']} · [{article['url']}]({article['url']})")
            st.write(summary)
            st.write(f"**Why it matters:** {article.get('why_it_matters', 'Connect this idea to healthcare data quality and trustworthy AI.')}")
            st.info(f"Key takeaway: {article['takeaways'][0]}")
        st.warning("Reflection: What data-quality risk could affect the main technique, and how would you mitigate it?")
    else:
        st.info("Click the button to generate a personalized brief from live sources with a local fallback.")

with tab2:
    st.header("nextLevelPersonalCoachForCareerLevel")
    st.write("Paste an internship description to make the assessment specific to that opportunity.")
    job_description = st.text_area("Job description", height=180, placeholder="Paste a healthcare AI or data science internship description here...")
    if job_description:
        skills = extract_required_skills(job_description)
        st.info("Detected requirements: " + (", ".join(skills) if skills else "No recognized keywords yet"))
    elif st.button("Find current opportunity leads", type="primary"):
        with st.spinner("Searching public opportunity results..."):
            results = discover_opportunities(profile)
        if results:
            st.success(f"Found {len(results)} relevant opportunity lead(s). Review the links and choose one for coaching.")
            for result in results[:5]:
                source = result.get("source", "Public search")
                skills = ", ".join(result.get("skills", []))
                st.markdown(f"### [{result['title']}]({result['url']})")
                st.caption(f"Source: {source} | Skills: {skills}")
        else:
            st.warning("No live results were returned. Paste a job description to run the assessment.")

    st.subheader("Technical assessment")
    with st.form("career_assessment"):
        answers = {}
        for index, question in enumerate(QUESTIONS):
            answers[index] = st.text_area(f"{index + 1}. {question['question']}", key=f"answer_{index}")
        submitted = st.form_submit_button("Evaluate my readiness", type="primary")
    if submitted:
        report = readiness_report(answers)
        record_coaching_session(report)
        st.metric("Readiness score", f"{report['overall_score_out_of_5']}/5")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Strengths")
            st.write(", ".join(report["strengths"]) or "Not demonstrated yet")
        with col2:
            st.subheader("Knowledge gaps")
            st.write(", ".join(report["knowledge_gaps"]) or "Continue practicing")
        st.subheader("Question-by-question feedback")
        for item in report["evaluations"]:
            st.write(f"**{item['competency']} — {item['score']}/5**")
            st.write(item["feedback"])
        st.subheader("Personalized improvement plan")
        for action in report["action_plan"]:
            st.write(f"- {action}")

with tab3:
    st.header("Progress and profile")
    st.subheader("Edit personalization")
    with st.form("profile_form"):
        interests = st.text_input("Interests", value=", ".join(profile["interests"]))
        growth = st.text_input("Growth areas", value=", ".join(profile["growth_areas"]))
        goal = st.text_input("Career goal", value=profile["career_goal"])
        daily_minutes = st.number_input("Daily learning minutes", min_value=5, max_value=120, value=int(profile["daily_minutes"]))
        save = st.form_submit_button("Save profile")
    if save:
        profile["interests"] = [item.strip() for item in interests.split(",") if item.strip()]
        profile["growth_areas"] = [item.strip() for item in growth.split(",") if item.strip()]
        profile["career_goal"] = goal
        profile["daily_minutes"] = daily_minutes
        save_profile(profile)
        st.success("Profile saved. Future rankings and coaching use these settings.")
    memory = load_memory()
    st.subheader("Learning memory")
    st.write(f"Articles saved: {len(memory['article_history'])}")
    st.write(f"Coaching sessions: {len(memory['coaching_sessions'])}")
    for session in memory["coaching_sessions"][-5:][::-1]:
        st.write(f"{session['timestamp']}: {session['score']}/5 — gaps: {', '.join(session['knowledge_gaps']) or 'none recorded'}")
