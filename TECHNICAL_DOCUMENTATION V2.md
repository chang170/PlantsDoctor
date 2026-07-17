# Plant Health AI — Technical Documentation

## 1. Application Overview

Plant Health AI is a web-based application that allows users to photograph or upload images of plants, trees, fruits, and vegetables to receive identification, health assessments, care recommendations, and detailed botanical information. The application uses a multimodal large language model (LLM) with vision capabilities to analyze images and return structured data.

---

## 2. Architecture

The application follows a client-server architecture with two independently deployed components:

```
┌─────────────────────────────┐         ┌──────────────────────────────┐
│   Frontend (Next.js PWA)    │  HTTPS  │    Backend (FastAPI)         │
│   Cloudflare Workers        │────────▶│    Render                    │
│                             │         │                              │
│ plantsdoctor.chi-sports.    │         │ plantsdoctor-uhrl.onrender.  │
│ workers.dev                 │         │ com                          │
└─────────────────────────────┘         └──────────┬───────────────────┘
                                                   │
                                                   │ API Call
                                                   ▼
                                        ┌──────────────────────┐
                                        │   Groq Cloud API     │
                                        │   (Llama 4 Vision)   │
                                        └──────────────────────┘
```

### Frontend
- **Framework**: Next.js 15.5 (React 19, TypeScript)
- **Hosting**: Cloudflare Workers via OpenNext adapter (@opennextjs/cloudflare)
- **Type**: Progressive Web App (PWA) — installable on mobile devices
- **URL**: `https://plantsdoctor.chi-sports.workers.dev`

### Backend
- **Framework**: FastAPI (Python)
- **Hosting**: Render (free tier web service)
- **URL**: `https://plantsdoctor-uhrl.onrender.com`
- **Dependencies**: fastapi, uvicorn, python-multipart, Pillow, groq

---

## 3. AI Model Architecture

### Model Used
- **Model**: Meta Llama 4 Scout 17B 16E Instruct
- **Model ID**: `meta-llama/llama-4-scout-17b-16e-instruct`
- **Capability**: Multimodal (text + vision)
- **Hosting**: Groq Cloud (inference API)
- **Training**: Pre-trained by Meta on diverse image and text data; instruction-tuned for structured output
- **Version**: Latest available through Groq API

### How the Model is Used
The application uses a single API call to Groq's chat completions endpoint with:
- A structured system prompt requesting JSON output
- The user's image encoded as base64 JPEG
- Temperature set to 0.3 for consistent results
- Max 2048 completion tokens

### What the Model Returns
The model analyzes the image and returns structured JSON containing:
- Plant identification (common name, scientific name, category)
- Geographic origin and alternative common names
- Health assessment (healthy/unhealthy, specific conditions)
- Care information (watering, sunlight, soil, toxicity, growth rate, mature size, season, difficulty)
- Fruit/vegetable specific data (ripeness, edibility, nutrition, storage tips)
- Fun facts

### Fallback Suggestion Engine
A rule-based `SuggestionEngine` class provides care suggestions for known plant diseases (bacterial spot, early/late blight, leaf mold, etc.) when the LLM does not return suggestions. This ensures users always receive actionable advice.

---

## 4. Data Flow

### Request Flow (Image Analysis)

1. **User uploads image** → Frontend (browser)
2. **Client-side compression** → Image resized to max 1024px, JPEG quality 80% (~200-400KB)
3. **POST /analyze** → FormData with compressed image sent to backend via HTTPS
4. **Backend receives image** → Opens with Pillow, converts to RGB
5. **Base64 encoding** → Image converted to base64 JPEG (quality 85%)
6. **Groq API call** → Image + structured prompt sent to Llama 4 Vision
7. **JSON parsing** → Model response parsed from JSON (handles markdown code blocks)
8. **Response structuring** → Data organized into plant, health, details, and suggestions objects
9. **JSON response** → Structured result returned to frontend
10. **UI rendering** → Frontend displays results in card-based layout

### Data Formats
- **Upload**: multipart/form-data (image file)
- **Internal**: PIL Image (RGB), base64-encoded JPEG
- **API communication**: JSON over HTTPS
- **Response structure**:
```json
{
  "plant": { "plant_name", "scientific_name", "origin", "category", "confidence", ... },
  "health": { "status", "condition", "confidence", "all_predictions" },
  "details": { "watering", "sunlight", "toxicity", "ripeness", "nutrition", ... },
  "suggestions": { "issue", "suggestions": [] }
}
```

---

## 5. Development and Deployment Workflow

### Repository Structure
```
PlantsDoctor/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models/
│   │   │   ├── health_analyzer.py   # Groq/Llama Vision integration
│   │   │   └── plant_classifier.py  # (Legacy) Transformer-based classifier
│   │   └── services/
│   │       └── suggestion_engine.py # Rule-based care suggestions
│   ├── requirements.txt
│   ├── Dockerfile
│   └── Procfile
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx             # Main application page
│   │   ├── layout.tsx           # Root layout
│   │   ├── globals.css          # Styles
│   │   └── install-prompt.tsx   # PWA install prompt
│   ├── package.json
│   ├── wrangler.toml            # Cloudflare Workers config
│   ├── open-next.config.ts      # OpenNext adapter config
│   └── next.config.js
├── README.md
├── DEPLOY.md
└── .gitignore
```

### Version Control
- **Platform**: GitHub
- **Repository**: `github.com/chang170/PlantsDoctor`
- **Branch strategy**: Single `main` branch (direct push workflow)
- **Commits**: Feature-based commit messages

### Deployment Pipeline

#### Backend (Render)
1. Developer pushes to `main` branch on GitHub
2. Render detects the push via GitHub webhook
3. Render builds from `backend/` root directory
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
6. Environment variable `GROQ_API_KEY` set in Render dashboard
7. Service goes live automatically

#### Frontend (Cloudflare Workers)
1. Developer pushes to `main` branch on GitHub
2. Cloudflare detects the push via GitHub integration
3. Build command: `npm install && npx opennextjs-cloudflare build`
4. Deploy command: `npx wrangler deploy`
5. OpenNext adapter compiles Next.js to Cloudflare Workers format
6. Static assets served from Workers assets directory
7. Environment variable `NEXT_PUBLIC_API_URL` set in `wrangler.toml` [vars]
8. Site goes live on workers.dev subdomain

### Environment Configuration
| Variable | Location | Purpose |
|----------|----------|---------|
| `GROQ_API_KEY` | Render (secret) | Authenticates with Groq API |
| `NEXT_PUBLIC_API_URL` | wrangler.toml / Cloudflare | Backend URL for frontend |
| `CLOUDFLARE_API_TOKEN` | Cloudflare (secret) | Authorizes Wrangler deployments |

### Uptime Management
- A cron job (via cron-job.org) pings `GET /health` every 10 minutes to prevent Render free tier from sleeping

---

## 6. Security, Privacy, and Reliability Considerations

### Data Handling
- **No persistent storage**: Images are processed in-memory only and never stored on the server
- **No user accounts**: No personal data is collected or stored
- **Transit encryption**: All communication is HTTPS (TLS)
- **Image compression**: Client-side compression reduces data transmitted
- **CORS**: Backend allows all origins (`*`) for cross-origin requests

### API Key Security
- `GROQ_API_KEY` is stored as an environment variable in Render's secret management, never committed to source code
- `CLOUDFLARE_API_TOKEN` is stored in Cloudflare's build environment

### Reliability
- **Free tier limitations**: Render free tier has 512MB RAM and sleeps after 15 minutes of inactivity
- **Cold start**: First request after sleep takes ~30 seconds
- **Rate limits**: Groq free tier allows 30 requests per minute
- **Timeout handling**: Frontend implements a 120-second timeout with user-friendly error messages
- **Graceful degradation**: If Groq API fails, error messages are displayed to the user

### AI Guardrails and Responsible AI Considerations

#### Model Limitations
- **Accuracy**: Llama 4 Vision is a general-purpose model, not a specialized botanical classifier. Identification accuracy varies and should not be relied upon for critical decisions (e.g., edibility of wild plants)
- **Hallucination risk**: LLMs can generate plausible but incorrect information, especially for rare or unusual species
- **Confidence scores**: The confidence value is self-reported by the LLM and may not correlate with actual accuracy
- **No medical/safety guarantee**: Toxicity and edibility information should be verified with authoritative sources before acting upon it

#### Recommended Safeguards
1. **Disclaimer**: Display a notice that AI results are informational only and should not replace expert botanical advice
2. **Edibility warning**: Clearly warn users never to consume plants based solely on AI identification
3. **Toxicity caution**: Emphasize that toxicity information requires verification from poison control or veterinary sources
4. **No PII in images**: Users should be aware that images are sent to Groq's cloud API (third-party service)
5. **Rate limiting**: Backend should implement rate limiting to prevent abuse
6. **Input validation**: Only image file types are accepted; images are validated through Pillow before processing
7. **Output sanitization**: JSON parsing includes error handling for malformed model responses

#### Potential Risks
| Risk | Severity | Mitigation |
|------|----------|------------|
| Misidentification of toxic plant as edible | High | Add prominent disclaimer; never state "safe to eat" without caveats |
| Model hallucinating care advice that harms plant | Low | Fallback suggestion engine provides validated common advice |
| User uploading non-plant images | Low | Model returns low-confidence results; no system harm |
| Groq API outage | Medium | Clear error messaging; no data loss since nothing is persisted |
| Image data sent to third-party (Groq) | Medium | Document in privacy policy; images processed ephemerally by Groq |

#### Governance Recommendations
- Add a visible disclaimer on the UI: "AI-generated results — verify before acting"
- Log failed requests for monitoring (without storing images)
- Periodically review Groq's data retention policies
- Consider adding a feedback mechanism for users to report incorrect identifications
- Review model updates when Groq changes available models

---

## 7. Technology Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend framework | Next.js | 15.5.x |
| UI library | React | 19.x |
| Language (frontend) | TypeScript | 5.5.x |
| Frontend hosting | Cloudflare Workers | — |
| Cloudflare adapter | @opennextjs/cloudflare | 1.x |
| Backend framework | FastAPI | latest |
| Language (backend) | Python | 3.11+ |
| Backend hosting | Render | Free tier |
| AI model | Llama 4 Scout 17B 16E Instruct | latest |
| AI inference platform | Groq Cloud | Free tier |
| Image processing | Pillow (PIL) | latest |
| Version control | Git / GitHub | — |
| Uptime monitoring | cron-job.org | — |

---

## 7. Security, Privacy, and Reliability Considerations

### Data Handling
- **No persistent storage**: Images are processed in-memory only and never stored on the server
- **No user accounts**: No personal data is collected or stored
- **Transit encryption**: All communication is HTTPS (TLS)
- **Image compression**: Client-side compression reduces data transmitted
- **CORS**: Backend allows all origins (`*`) for cross-origin requests

### API Key Security
- `GROQ_API_KEY` is stored as an environment variable in Render's secret management, never committed to source code
- `CLOUDFLARE_API_TOKEN` is stored in Cloudflare's build environment

### Reliability
- **Free tier limitations**: Render free tier has 512MB RAM and sleeps after 15 minutes of inactivity
- **Cold start**: First request after sleep takes ~30 seconds
- **Rate limits**: Groq free tier allows 30 requests per minute
- **Timeout handling**: Frontend implements a 120-second timeout with user-friendly error messages
- **Graceful degradation**: If Groq API fails, error messages are displayed to the user

### AI Guardrails and Responsible AI Considerations

#### Model Limitations
- **Accuracy**: Llama 4 Vision is a general-purpose model, not a specialized botanical classifier. Identification accuracy varies and should not be relied upon for critical decisions (e.g., edibility of wild plants)
- **Hallucination risk**: LLMs can generate plausible but incorrect information, especially for rare or unusual species
- **Confidence scores**: The confidence value is self-reported by the LLM and may not correlate with actual accuracy
- **No medical/safety guarantee**: Toxicity and edibility information should be verified with authoritative sources before acting upon it

#### Recommended Safeguards
1. **Disclaimer**: Display a notice that AI results are informational only and should not replace expert botanical advice
2. **Edibility warning**: Clearly warn users never to consume plants based solely on AI identification
3. **Toxicity caution**: Emphasize that toxicity information requires verification from poison control or veterinary sources
4. **No PII in images**: Users should be aware that images are sent to Groq's cloud API (third-party service)
5. **Rate limiting**: Backend should implement rate limiting to prevent abuse
6. **Input validation**: Only image file types are accepted; images are validated through Pillow before processing
7. **Output sanitization**: JSON parsing includes error handling for malformed model responses

#### Potential Risks
| Risk | Severity | Mitigation |
|------|----------|------------|
| Misidentification of toxic plant as edible | High | Add prominent disclaimer; never state "safe to eat" without caveats |
| Model hallucinating care advice that harms plant | Low | Fallback suggestion engine provides validated common advice |
| User uploading non-plant images | Low | Model returns low-confidence results; no system harm |
| Groq API outage | Medium | Clear error messaging; no data loss since nothing is persisted |
| Image data sent to third-party (Groq) | Medium | Document in privacy policy; images processed ephemerally by Groq |

#### Governance Recommendations
- Add a visible disclaimer on the UI: "AI-generated results — verify before acting"
- Log failed requests for monitoring (without storing images)
- Periodically review Groq's data retention policies
- Consider adding a feedback mechanism for users to report incorrect identifications
- Review model updates when Groq changes available models

---

## 8. Technology Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend framework | Next.js | 15.5.x |
| UI library | React | 19.x |
| Language (frontend) | TypeScript | 5.5.x |
| Frontend hosting | Cloudflare Workers | — |
| Cloudflare adapter | @opennextjs/cloudflare | 1.x |
| Backend framework | FastAPI | latest |
| Language (backend) | Python | 3.11+ |
| Backend hosting | Render | Free tier |
| AI model | Llama 4 Scout 17B 16E Instruct | latest |
| AI inference platform | Groq Cloud | Free tier |
| Image processing | Pillow (PIL) | latest |
| Version control | Git / GitHub | — |
| Uptime monitoring | cron-job.org | — |
