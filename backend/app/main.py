from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.models.plant_classifier import PlantClassifier
from app.models.health_analyzer import HealthAnalyzer
from app.services.suggestion_engine import SuggestionEngine
from PIL import Image
import io
import traceback

app = FastAPI(title="Plant Health AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

plant_classifier = PlantClassifier()
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

        # Step 1: Analyze with vision LLM (does both ID and health)
        health_result = health_analyzer.predict(image)

        # Step 2: Use the LLM's plant identification if available
        llm_plant_name = health_result.pop("plant_name_from_health", "")
        llm_suggestions = health_result.pop("suggestions_from_llm", [])

        # Step 3: Also run the dedicated plant classifier
        plant_result = plant_classifier.predict(image)

        # Prefer LLM plant name if classifier confidence is low
        if llm_plant_name and plant_result["confidence"] < 0.5:
            plant_result["plant_name"] = llm_plant_name

        # Step 4: Get care suggestions
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
            "suggestions": suggestions,
        }
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )
