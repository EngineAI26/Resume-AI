# 🎯 ResumeAI — Career Fit Analyzer

> A **100% Python** Streamlit app — upload your resume + paste a job description → get an AI fit score, gap analysis, and a tailored resume PDF.

**No HTML. No JavaScript. Pure Python.** ✅

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Resume Upload** | Supports PDF and TXT resumes |
| 🎯 **Fit Score** | 0–100% match score with color-coded verdict |
| ✅ **Strengths** | What already makes you a strong candidate |
| ⚠️ **Gap Analysis** | Skills and experience you're missing |
| 💡 **Recommendations** | Actionable steps to improve your application |
| 🔑 **ATS Keywords** | Keywords from the job description you're missing |
| 📝 **Optimized Resume** | Full resume rewritten by AI for this specific role |
| ⬇️ **PDF Download** | Download your tailored resume as a professional PDF |

---

## 🛠️ Tech Stack (100% Python)

| Library | Purpose |
|---|---|
| `streamlit` | Web UI — zero HTML needed |
| `google-generativeai` | Gemini 2.0 Flash API (free) |
| `PyMuPDF` | Extract text from PDF resumes |
| `reportlab` | Generate the optimized PDF resume |

---

## 🔑 Step 1: Get Your Free Gemini API Key

1. Go to **[aistudio.google.com/apikey](https://aistudio.google.com/apikey)**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)

> Free tier: 15 requests/minute — more than enough for personal use.

---

## 🚀 Step 2: Run Locally

```bash
# Clone this repo
git clone https://github.com/YOUR_USERNAME/resume-ai.git
cd resume-ai

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Your browser will open at `http://localhost:8501` automatically.

---

## ☁️ Step 3: Deploy to Streamlit Cloud (Free, 5 mins)

### Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: ResumeAI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/resume-ai.git
git push -u origin main
```

### Deploy on Streamlit Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"New app"**
3. Select your GitHub repo
4. Set **Main file path** to `app.py`
5. Click **"Deploy"**

Your app will be live at:
`https://YOUR_USERNAME-resume-ai-app-XXXXX.streamlit.app`

---

## 📁 Project Structure

```
resume-ai/
├── app.py              # 🐍 The entire application (pure Python)
├── requirements.txt    # Dependencies
└── README.md           # This file
```

---

## 🔒 Privacy

- Your API key is typed directly into the app and **never stored**
- Resume text is sent **only to Google's Gemini API** — no other server sees it
- No database, no user accounts, no tracking

---

## 📄 License

MIT © 2025 — Free to use and modify.
