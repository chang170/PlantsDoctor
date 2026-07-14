# Deployment Guide (100% Free)

## Step 1: Deploy Backend to Hugging Face Spaces

1. Create a free account at [huggingface.co](https://huggingface.co)
2. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
3. Fill in:
   - **Space name**: `plant-health-ai`
   - **SDK**: Docker
   - **Visibility**: Public (required for free tier)
4. Clone the Space repo and copy the `backend/` contents into it:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/plant-health-ai
   cp -r backend/* plant-health-ai/
   cd plant-health-ai
   git add .
   git commit -m "Initial deploy"
   git push
   ```
5. Wait a few minutes for it to build
6. Your API is now live at: `https://YOUR_USERNAME-plant-health-ai.hf.space`

Test it:
```bash
curl https://YOUR_USERNAME-plant-health-ai.hf.space/health
```

## Step 2: Deploy Frontend to Cloudflare Pages

1. Log into [dash.cloudflare.com](https://dash.cloudflare.com)
2. Go to **Workers & Pages** → **Create** → **Pages**
3. Connect your GitHub/GitLab repo (or upload directly)
4. Set build settings:
   - **Root directory**: `frontend`
   - **Build command**: `npm run build`
   - **Output directory**: `.next`
   - **Framework preset**: Next.js
5. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://YOUR_USERNAME-plant-health-ai.hf.space`
6. Deploy!

Your app is now live at: `https://plant-health-ai.pages.dev`

## Step 3: Custom Domain (Optional, Free)

If you have a domain on Cloudflare:
1. Go to your Pages project → **Custom domains**
2. Add your domain (e.g., `plantdoc.yourdomain.com`)
3. Cloudflare handles SSL automatically

## Architecture

```
Users (phone/browser)
       │
       ▼
Cloudflare Pages (frontend PWA)
  - plant-health-ai.pages.dev
  - Global CDN, instant loads
  - FREE
       │
       ▼
Hugging Face Spaces (backend API)
  - YOUR_USERNAME-plant-health-ai.hf.space
  - Runs AI models (16GB RAM)
  - FREE
```

## Notes

- HF Spaces sleeps after ~15 min of inactivity (cold start ~30s)
- Cloudflare Pages has unlimited bandwidth on free tier
- Models are cached on HF after first load
- No credit card required for either service
