class SuggestionEngine:
    """Maps plant conditions to care suggestions."""

    CONDITION_SUGGESTIONS = {
        "bacterial_spot": {
            "issue": "Bacterial infection on leaves",
            "suggestions": [
                "Remove infected leaves immediately",
                "Reduce overhead watering to keep leaves dry",
                "Improve air circulation around the plant",
                "Apply copper-based bactericide",
            ],
        },
        "early_blight": {
            "issue": "Fungal infection (early blight)",
            "suggestions": [
                "Remove affected lower leaves",
                "Avoid watering from above",
                "Apply fungicide (chlorothalonil or copper-based)",
                "Ensure proper spacing between plants",
            ],
        },
        "late_blight": {
            "issue": "Fungal infection (late blight)",
            "suggestions": [
                "Remove and destroy infected plants",
                "Apply fungicide immediately",
                "Avoid overhead irrigation",
                "Improve drainage in soil",
            ],
        },
        "leaf_mold": {
            "issue": "Leaf mold (fungal)",
            "suggestions": [
                "Increase air circulation",
                "Reduce humidity around the plant",
                "Remove affected leaves",
                "Apply fungicide if severe",
            ],
        },
        "septoria_leaf_spot": {
            "issue": "Septoria leaf spot (fungal)",
            "suggestions": [
                "Remove infected leaves at first sign",
                "Avoid wetting foliage when watering",
                "Apply fungicide preventatively",
                "Mulch around base to prevent soil splash",
            ],
        },
        "spider_mites": {
            "issue": "Spider mite infestation",
            "suggestions": [
                "Spray leaves with water to dislodge mites",
                "Apply neem oil or insecticidal soap",
                "Increase humidity around the plant",
                "Isolate affected plant from others",
            ],
        },
        "target_spot": {
            "issue": "Target spot (fungal)",
            "suggestions": [
                "Remove affected leaves",
                "Improve air circulation",
                "Apply appropriate fungicide",
                "Avoid overhead watering",
            ],
        },
        "yellow_leaf_curl_virus": {
            "issue": "Yellow leaf curl virus",
            "suggestions": [
                "Remove and destroy infected plants",
                "Control whitefly populations (virus carriers)",
                "Use reflective mulch to repel whiteflies",
                "Plant resistant varieties in future",
            ],
        },
        "mosaic_virus": {
            "issue": "Mosaic virus infection",
            "suggestions": [
                "Remove and destroy infected plants",
                "Disinfect tools after handling infected plants",
                "Control aphid populations",
                "Plant virus-resistant varieties",
            ],
        },
    }

    DEFAULT_HEALTHY = {
        "issue": "No issues detected",
        "suggestions": [
            "Continue regular watering schedule",
            "Ensure adequate sunlight",
            "Fertilize according to plant needs",
            "Monitor for any changes",
        ],
    }

    DEFAULT_UNHEALTHY = {
        "issue": "General plant stress detected",
        "suggestions": [
            "Check soil moisture — may need more or less water",
            "Verify light conditions are appropriate for this plant",
            "Check for nutrient deficiency — consider balanced fertilizer",
            "Inspect for pests on undersides of leaves",
            "Ensure proper drainage to avoid root rot",
        ],
    }

    DEFAULT_UNKNOWN = {
        "issue": "Plant type not in health database",
        "suggestions": [
            "The health model doesn't cover this plant species yet",
            "Visually check for yellowing, wilting, or spots on leaves",
            "Ensure soil is moist but not waterlogged",
            "Make sure the plant gets appropriate light for its type",
            "Look for pests on the undersides of leaves",
        ],
    }

    def get_suggestions(self, plant_name: str, health_status: str, condition: str) -> dict:
        """Get care suggestions based on plant condition."""
        if health_status == "healthy":
            return self.DEFAULT_HEALTHY

        if health_status == "unknown":
            return self.DEFAULT_UNKNOWN

        # Try to match condition to known conditions
        condition_lower = condition.lower().replace(" ", "_")
        for key, value in self.CONDITION_SUGGESTIONS.items():
            if key in condition_lower:
                return value

        return self.DEFAULT_UNHEALTHY
