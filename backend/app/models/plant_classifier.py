from transformers import pipeline
from PIL import Image


class PlantClassifier:
    """Identifies plant species from an image using a pre-trained model."""

    def __init__(self):
        self.model = None

    def _load_model(self):
        if self.model is None:
            self.model = pipeline(
                "image-classification",
                model="dima806/house-plant-image-detection",
            )

    def predict(self, image: Image.Image) -> dict:
        """Predict plant species from an image."""
        self._load_model()
        results = self.model(image)
        top_result = results[0]
        return {
            "plant_name": top_result["label"],
            "confidence": round(top_result["score"], 3),
            "all_predictions": [
                {"name": r["label"], "confidence": round(r["score"], 3)}
                for r in results[:5]
            ],
        }
