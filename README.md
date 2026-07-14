# 🌿 Plant Health AI

AI-powered plant identification and health analysis. Take a photo of your plant
to identify the species, check its health, and get care suggestions.

## Architecture

- **Frontend**: Next.js PWA (TypeScript) — installable on any phone
- **Backend**: FastAPI (Python) — runs AI models for plant analysis

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at http://localhost:3000

## How It Works

1. User takes/uploads a photo of their plant
2. Image is sent to the backend API
3. **Plant Classifier** identifies the species
4. **Health Analyzer** detects diseases or issues
5. **Suggestion Engine** provides care recommendations
6. Results displayed to the user

## AI Models Used (Free, Open Source)

- Plant ID: [dima806/house-plant-image-detection](https://huggingface.co/dima806/house-plant-image-detection)
- Health: [14maddy/plant_disease-mobilenetv2](https://huggingface.co/14maddy/plant_disease-mobilenetv2)

## Deployment (Free)

- Frontend: Deploy to [Vercel](https://vercel.com) (free tier)
- Backend: Deploy to [Render](https://render.com) or [Hugging Face Spaces](https://huggingface.co/spaces)
