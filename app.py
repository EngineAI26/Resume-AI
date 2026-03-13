import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import json
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeAI – Career Fit Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# Custom CSS (minimal, only for tweaks Streamlit can't do natively)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .score-box {
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        margin-bottom: 16px;
    }
    .big-score { font-size: 72px; font-weight: 900; line-height: 1; }
    .verdict   { font-size: 20px; font-weight: 600; margin-top: 8px; }
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        margin: 3px;
    }
    .tag-green  { background:#d1fae5; color:#065f46; }
    .tag-red    { background:#fee2e2; color:#991b1b; }
    .tag-yellow { background:#fef9c3; color:#854d0e; }
    div[data-testid="stExpander"] { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract plain text from a PDF using PyMuPDF."""
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()


def extract_text_from_txt(uploaded_file) -> str:
    return uploaded_file.read().decode("utf-8", errors="ignore")


def call_gemini(api_key: str, resume_text: str, company: str, job_title: str, job_desc: str) -> dict:
    """Call Gemini API and return parsed JSON response."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""You are an expert career coach and ATS specialist.

Analyze the candidate's resume against the job posting below.
Respond ONLY with a valid JSON object — no markdown, no extra text.

RESUME:
{resume_text}

COMPANY: {company or "Not specified"}
JOB TITLE: {job_title or "Not specified"}
JOB DESCRIPTION:
{job_desc}

Return EXACTLY this JSON structure:
{{
  "fit_score": <integer 0-100>,
  "verdict": "<e.g. Strong Match | Moderate Fit | Weak Alignment>",
  "summary": "<2-3 honest sentences about this candidate's overall fit>",
  "matching_skills": ["skill1", "skill2", "skill3"],
  "skill_gaps": ["gap1", "gap2", "gap3"],
  "partial_matches": ["partial1", "partial2"],
  "strengths": ["strength detail 1", "strength detail 2", "strength detail 3", "strength detail 4"],
  "gaps": ["gap detail 1", "gap detail 2", "gap detail 3"],
  "recommendations": ["actionable rec 1", "actionable rec 2", "actionable rec 3", "actionable rec 4"],
  "keywords_to_add": ["kw1", "kw2", "kw3", "kw4", "kw5", "kw6"],
  "optimized_resume": {{
    "name": "<candidate full name>",
    "contact": "<email | phone | location | linkedin>",
    "summary": "<Tailored 3-4 sentence professional summary for this exact role>",
    "experience": [
      {{
        "title": "<Job Title>",
        "company": "<Company>",
        "dates": "<Date Range>",
        "bullets": ["<achievement 1 with metrics>", "<achievement 2>", "<achievement 3>"]
      }}
    ],
    "education": [
      {{
        "degree": "<Degree>",
        "school": "<University/College>",
        "year": "<Year>"
      }}
    ],
    "skills": ["skill1", "skill2", "skill3", "skill4", "skill5", "skill6", "skill7", "skill8"],
    "certifications": ["cert1", "cert2"]
  }}
}}"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown fences if present
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


def build_pdf(data: dict, company: str, job_title: str) -> bytes:
    """Build a beautifully formatted PDF resume using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )

    resume = data.get("optimized_resume", {})
    accent = colors.HexColor("#4f46e5")   # indigo
    dark   = colors.HexColor("#1e1b4b")
    gray   = colors.HexColor("#6b7280")
    light_bg = colors.HexColor("#eef2ff")

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "Name", fontSize=26, textColor=dark,
        fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4
    )
    contact_style = ParagraphStyle(
        "Contact", fontSize=9, textColor=gray,
        fontName="Helvetica", alignment=TA_CENTER, spaceAfter=10
    )
    section_style = ParagraphStyle(
        "Section", fontSize=10, textColor=accent,
        fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4,
        textTransform="uppercase", letterSpacing=1.5
    )
    body_style = ParagraphStyle(
        "Body", fontSize=10, textColor=dark,
        fontName="Helvetica", spaceAfter=3, leading=14
    )
    bullet_style = ParagraphStyle(
        "Bullet", fontSize=10, textColor=colors.HexColor("#374151"),
        fontName="Helvetica", leftIndent=12, spaceAfter=2,
        leading=14, bulletIndent=0
    )
    job_title_style = ParagraphStyle(
        "JobTitle", fontSize=11, textColor=dark,
        fontName="Helvetica-Bold", spaceAfter=1
    )
    company_style = ParagraphStyle(
        "Company", fontSize=10, textColor=gray,
        fontName="Helvetica-Oblique", spaceAfter=4
    )
    footer_style = ParagraphStyle(
        "Footer", fontSize=8, textColor=gray,
        fontName="Helvetica", alignment=TA_CENTER
    )

    story = []

    # ── Header banner ────────────────────────────────────────────────
    from reportlab.platypus import Table, TableStyle
    banner_text = f"Optimized for: {job_title or 'Target Role'} @ {company or 'Company'}"
    banner = Table([[Paragraph(banner_text, ParagraphStyle(
        "Banner", fontSize=8, textColor=colors.white,
        fontName="Helvetica-Bold", alignment=TA_CENTER
    ))]], colWidths=[174 * mm])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), accent),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(banner)
    story.append(Spacer(1, 10))

    # ── Name & Contact ───────────────────────────────────────────────
    story.append(Paragraph(resume.get("name", "Your Name"), name_style))
    story.append(Paragraph(resume.get("contact", ""), contact_style))
    story.append(HRFlowable(width="100%", thickness=2, color=accent, spaceAfter=8))

    # ── Professional Summary ─────────────────────────────────────────
    if resume.get("summary"):
        story.append(Paragraph("Professional Summary", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#c7d2fe"), spaceAfter=6))
        story.append(Paragraph(resume["summary"], body_style))

    # ── Experience ───────────────────────────────────────────────────
    if resume.get("experience"):
        story.append(Paragraph("Experience", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#c7d2fe"), spaceAfter=6))
        for job in resume["experience"]:
            story.append(Paragraph(job.get("title", ""), job_title_style))
            company_dates = f"{job.get('company', '')}  •  {job.get('dates', '')}"
            story.append(Paragraph(company_dates, company_style))
            for bullet in job.get("bullets", []):
                story.append(Paragraph(f"• {bullet}", bullet_style))
            story.append(Spacer(1, 6))

    # ── Education ────────────────────────────────────────────────────
    if resume.get("education"):
        story.append(Paragraph("Education", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#c7d2fe"), spaceAfter=6))
        for edu in resume["education"]:
            degree_line = f"<b>{edu.get('degree', '')}</b> — {edu.get('school', '')}  ({edu.get('year', '')})"
            story.append(Paragraph(degree_line, body_style))

    # ── Skills ───────────────────────────────────────────────────────
    if resume.get("skills"):
        story.append(Paragraph("Skills", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#c7d2fe"), spaceAfter=6))
        skills_text = "  •  ".join(resume["skills"])
        story.append(Paragraph(skills_text, body_style))

    # ── Certifications ───────────────────────────────────────────────
    if resume.get("certifications"):
        story.append(Paragraph("Certifications", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#c7d2fe"), spaceAfter=6))
        for cert in resume["certifications"]:
            story.append(Paragraph(f"• {cert}", bullet_style))

    # ── Footer ───────────────────────────────────────────────────────
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb"), spaceAfter=4))
    story.append(Paragraph("Generated by ResumeAI — Powered by Google Gemini", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def score_color(score: int):
    if score >= 70:
        return "#d1fae5", "#065f46"   # green bg, dark green text
    elif score >= 45:
        return "#fef9c3", "#854d0e"   # yellow
    else:
        return "#fee2e2", "#991b1b"   # red


# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────

st.title("🎯 ResumeAI — Career Fit Analyzer")
st.markdown("Upload your resume + paste a job description → get an **AI fit score**, gap analysis, and a **tailored resume PDF** you can download.")

st.divider()

# ── API Key ──────────────────────────────────────────────────────────
with st.expander("🔑 Enter your free Google Gemini API Key", expanded=True):
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="AIza...",
        help="Get a FREE key at https://aistudio.google.com/apikey"
    )
    st.caption("🔒 Your key is used only to call Google's API directly. It is never stored.")

st.divider()

# ── Two-column input ─────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📄 Your Resume")
    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "txt"],
        help="Supports PDF and plain text files"
    )
    if uploaded_file:
        st.success(f"✅ Loaded: **{uploaded_file.name}**")

with col2:
    st.subheader("🏢 Job Details")
    company_name = st.text_input("Company Name", placeholder="e.g. Google, Stripe, OpenAI")
    job_title    = st.text_input("Job Title",    placeholder="e.g. Senior Data Scientist")
    job_desc     = st.text_area(
        "Paste the Job Description",
        height=220,
        placeholder="Paste the full job description here..."
    )

st.divider()

# ── Analyze button ───────────────────────────────────────────────────
analyze_clicked = st.button("✦ Analyze My Fit", type="primary", use_container_width=True)

if analyze_clicked:
    # Validate inputs
    errors = []
    if not api_key:        errors.append("Please enter your Gemini API key.")
    if not uploaded_file:  errors.append("Please upload your resume.")
    if not job_desc.strip(): errors.append("Please paste the job description.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        # Extract resume text
        with st.spinner("Reading your resume..."):
            if uploaded_file.name.endswith(".pdf"):
                resume_text = extract_text_from_pdf(uploaded_file)
            else:
                resume_text = extract_text_from_txt(uploaded_file)

        if len(resume_text.strip()) < 50:
            st.error("Could not extract enough text from your resume. Try a text-based PDF.")
            st.stop()

        # Call Gemini
        with st.spinner("🤖 Gemini is analyzing your profile… (this takes ~15 seconds)"):
            try:
                result = call_gemini(api_key, resume_text, company_name, job_title, job_desc)
            except json.JSONDecodeError:
                st.error("The AI returned an unexpected format. Please try again.")
                st.stop()
            except Exception as ex:
                st.error(f"API Error: {ex}")
                st.stop()

        # ── RESULTS ─────────────────────────────────────────────────
        st.success("✅ Analysis complete!")
        st.divider()
        st.header("📊 Your Results")

        score = result.get("fit_score", 0)
        verdict = result.get("verdict", "")
        summary = result.get("summary", "")
        bg, fg = score_color(score)

        # Score card
        st.markdown(f"""
        <div class="score-box" style="background:{bg};">
            <div class="big-score" style="color:{fg};">{score}%</div>
            <div class="verdict" style="color:{fg};">{verdict}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"> {summary}")

        # Skill tags
        st.markdown("**Matching Skills:**")
        tags_html = ""
        for s in result.get("matching_skills", []):
            tags_html += f'<span class="tag tag-green">{s}</span>'
        for s in result.get("partial_matches", []):
            tags_html += f'<span class="tag tag-yellow">{s}</span>'
        for s in result.get("skill_gaps", []):
            tags_html += f'<span class="tag tag-red">{s}</span>'
        st.markdown(tags_html, unsafe_allow_html=True)

        st.divider()

        # ── 4 analysis columns ───────────────────────────────────────
        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)

        with c1:
            st.subheader("✅ Strengths")
            for item in result.get("strengths", []):
                st.markdown(f"- {item}")

        with c2:
            st.subheader("⚠️ Gaps to Address")
            for item in result.get("gaps", []):
                st.markdown(f"- {item}")

        with c3:
            st.subheader("💡 Recommendations")
            for item in result.get("recommendations", []):
                st.markdown(f"- {item}")

        with c4:
            st.subheader("🔑 Keywords to Add")
            for kw in result.get("keywords_to_add", []):
                st.markdown(f"- `{kw}`")

        st.divider()

        # ── Optimized Resume Preview ─────────────────────────────────
        st.subheader("📝 Your Optimized Resume")
        st.caption("Rewritten by AI to maximize your ATS score for this specific role.")

        opt = result.get("optimized_resume", {})

        with st.container(border=True):
            st.markdown(f"## {opt.get('name', '')}")
            st.caption(opt.get("contact", ""))
            st.markdown("---")

            if opt.get("summary"):
                st.markdown("**PROFESSIONAL SUMMARY**")
                st.write(opt["summary"])

            if opt.get("experience"):
                st.markdown("**EXPERIENCE**")
                for job in opt["experience"]:
                    st.markdown(f"**{job.get('title','')}** — *{job.get('company','')}* &nbsp;&nbsp; `{job.get('dates','')}`")
                    for b in job.get("bullets", []):
                        st.markdown(f"  - {b}")

            if opt.get("education"):
                st.markdown("**EDUCATION**")
                for edu in opt["education"]:
                    st.markdown(f"- **{edu.get('degree','')}** — {edu.get('school','')} ({edu.get('year','')})")

            if opt.get("skills"):
                st.markdown("**SKILLS**")
                st.write("  •  ".join(opt["skills"]))

            if opt.get("certifications"):
                st.markdown("**CERTIFICATIONS**")
                for c in opt["certifications"]:
                    st.markdown(f"- {c}")

        # ── PDF Download ─────────────────────────────────────────────
        with st.spinner("Generating your PDF..."):
            pdf_bytes = build_pdf(result, company_name, job_title)

        candidate_name = opt.get("name", "Resume").replace(" ", "_")
        st.download_button(
            label="⬇️ Download Optimized Resume as PDF",
            data=pdf_bytes,
            file_name=f"{candidate_name}_Optimized.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
