<<<<<<< HEAD
# CivicAgent — Complete Multi-Agent Civic Intelligence

CivicAgent is a Generative + Agentic AI architecture for autonomous civic issue analysis.

## Agent pipeline

Citizen report → Orchestrator → Vision → Research → Safety & Impact → Multi-Agent Debate → Decision → Action

## Important

The architecture is AI-first. If `OPENAI_API_KEY` is configured, every agent uses the central AI provider.

If the key is not configured, the same agent interfaces use deterministic development fallbacks so the entire application can be developed and tested without API credits. The UI never claims those fallbacks are live AI.

## Windows setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and add your key when billing is available.

Run:

```powershell
uvicorn backend.main:app --reload
```

Open:

http://127.0.0.1:8000

## Hackathon demo

Use a description such as:

"Large pothole filled with water on a busy road near the college entrance. Motorcycles and cars pass through this area every day."

Then upload a road/pothole image and submit.

## Security

Never commit `.env` or an API key to GitHub.
=======
# Civic-Agent
>>>>>>> f18377cd98c1b4667fe68393585d5d3037f03bd7
