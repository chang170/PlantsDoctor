from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.models.health_analyzer import HealthAnalyzer
from app.services.suggestion_engine import SuggestionEngine
from PIL import Image
import io
import traceback

app = FastAPI(title="Plant Health AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

health_analyzer = HealthAnalyzer()
suggestion_engine = SuggestionEngine()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_plant(file: UploadFile = File(...)):
    """Analyze a plant image for species identification and health assessment."""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Analyze with vision LLM (does both ID and health)
        health_result = health_analyzer.predict(image)

        # Extract plant identification and suggestions
        llm_plant_name = health_result.pop("plant_name_from_health", "")
        llm_suggestions = health_result.pop("suggestions_from_llm", [])

        plant_result = {
            "plant_name": llm_plant_name or "Unknown",
            "scientific_name": health_result.pop("scientific_name", ""),
            "other_common_names": health_result.pop("other_common_names", []),
            "origin": health_result.pop("origin", ""),
            "category": health_result.pop("category", ""),
            "confidence": health_result.get("confidence", 0.8),
            "all_predictions": [],
        }

        # Plant care details
        details = {
            "watering": health_result.pop("watering", ""),
            "sunlight": health_result.pop("sunlight", ""),
            "soil_type": health_result.pop("soil_type", ""),
            "toxicity": health_result.pop("toxicity", ""),
            "growth_rate": health_result.pop("growth_rate", ""),
            "mature_size": health_result.pop("mature_size", ""),
            "season": health_result.pop("season", ""),
            "difficulty": health_result.pop("difficulty", ""),
            "fun_fact": health_result.pop("fun_fact", ""),
            "ripeness": health_result.pop("ripeness", None),
            "edibility": health_result.pop("edibility", None),
            "nutrition": health_result.pop("nutrition", None),
            "storage_tips": health_result.pop("storage_tips", None),
        }

        # Get care suggestions
        if llm_suggestions:
            suggestions = {
                "issue": health_result["condition"],
                "suggestions": llm_suggestions,
            }
        else:
            suggestions = suggestion_engine.get_suggestions(
                plant_name=plant_result["plant_name"],
                health_status=health_result["status"],
                condition=health_result["condition"],
            )

        return {
            "plant": plant_result,
            "health": health_result,
            "details": details,
            "suggestions": suggestions,
        }
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@app.post("/ask")
async def ask_followup(body: dict):
    """Answer a follow-up question about an already-analyzed plant."""
    try:
        question = body.get("question", "")
        context = body.get("context", {})

        answer = health_analyzer.ask_question_text(question, context)
        return {"answer": answer}
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )
