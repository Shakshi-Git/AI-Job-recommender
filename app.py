import streamlit as st
from src.helper import extract_text_from_pdf, ask_google_genai
from src.job_api import fetch_linkedin_jobs


st.set_page_config(page_title="Job Recommender", layout="wide")
st.title("📄 AI Job Recommender (Gemini)")
st.markdown("Upload your resume and get job recommendations based on your skills and experience from LinkedIn")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    with st.spinner("Summarizing your resume..."):
        summary = ask_google_genai(
            f"Summarize this resume highlighting the skills, education, and experience:\n\n{resume_text}",
            max_tokens=500
        )

    with st.spinner("Finding skill gaps..."):
        gaps = ask_google_genai(
            f"Analyze this resume and highlight missing skills, certifications, and experiences needed for better job opportunities:\n\n{resume_text}",
            max_tokens=400
        )

    with st.spinner("Creating future roadmap..."):
        roadmap = ask_google_genai(
            f"Based on this resume, suggest a future roadmap to improve this person's career prospects "
            f"(skills to learn, certifications needed, industry exposure):\n\n{resume_text}",
            max_tokens=400
        )

    # Display nicely formatted results
    st.markdown("---")
    st.header("📑 Resume Summary")
    st.markdown(
        f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; "
        f"font-size:16px; color:white;'>{summary}</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.header("🛠️ Skill Gaps & Missing Areas")
    st.markdown(
        f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; "
        f"font-size:16px; color:white;'>{gaps}</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.header("🚀 Future Roadmap & Preparation Strategy")
    st.markdown(
        f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; "
        f"font-size:16px; color:white;'>{roadmap}</div>",
        unsafe_allow_html=True
    )

    st.success("✅ Analysis Completed Successfully!")

    if st.button("🔎 Get Job Recommendations"):
        with st.spinner("Fetching job recommendations..."):
            keywords = ask_google_genai(
                f"You are a career advisor. Based on the resume summary below, generate a highly relevant, comma-separated list of specific job titles that match the candidates skills, work experience, industry background and education."
                f"Give a comma-separated list only, no explanation.\n\nSummary: {summary}",
                max_tokens=100
            )
            search_keywords_clean = keywords.split(",")[0].strip()

        st.success(f"Extracted Job Keywords: {search_keywords_clean}")

        with st.spinner("Fetching jobs from LinkedIn..."):
            linkedin_jobs = fetch_linkedin_jobs(search_keywords_clean, rows=60)


        st.markdown("---")
        st.header("💼 Top LinkedIn Jobs")

        if linkedin_jobs:
            for job in linkedin_jobs:
                st.markdown(f"**{job.get('title')}** at *{job.get('companyName')}*")
                st.markdown(f"- 📍 {job.get('location')}")
                st.markdown(f"- 🔗 [View Job]({job.get('link')})")
                st.markdown("---")
        else:
            st.warning("No LinkedIn jobs found.")

       

