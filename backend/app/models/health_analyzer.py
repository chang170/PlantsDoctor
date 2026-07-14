import base64
import json
import os
from io import BytesIO
from PIL import Image

try:
    from groq import Groq
except ImportError:
    Groq = None


class HealthAnalyzer:
    """Analyzes plant health using Groq's free Llama Vision API.

    Works with ANY plant — flowers, houseplants, weeds, crops, trees.
    Free tier: 30 requests/minute, no credit card required.
    """

    MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

    PROMPT = """You are a plant health expert. Analyze this image and provide:

1. What type of plant this is (species or common name)
2. Whether the plant looks healthy or unhealthy
3. If unhealthy, what specific problems you see
4. Care suggestions based on what you observe

Respond in this exact JSON format (no markdown, no extra text):
{
  "plant_name": "common name of the plant",
  "status": "healthy" or "unhealthy",
  "condition": "brief description of the condition",
  "confidence": 0.0 to 1.0,
  "problems": ["list of problems if any"],
  "suggestions": ["list of care suggestions"]
}"""

    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if Groq and api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None

    def predict(self, image: Image.Image) -> dict:
        """Assess plant health from an image using vision LLM."""
        if not self.client:
            return {
                "status": "error",
                "condition": "GROQ_API_KEY not set",
                "confidence": 0.0,
                "all_predictions": [],
            }

        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

        try:
            completion = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                temperature=0.3,
                max_completion_tokens=1024,
            )

            response_text = completion.choices[0].message.content.strip()

            # Parse JSON from response
            # Handle case where model wraps in markdown code block
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            data = json.loads(response_text)

            return {
                "status": data.get("status", "unknown"),
                "condition": data.get("condition", "Unknown"),
                "confidence": data.get("confidence", 0.8),
                "all_predictions": [
                    {"condition": p, "confidence": 0.8}
                    for p in data.get("problems", [])
                ],
                "plant_name_from_health": data.get("plant_name", ""),
                "suggestions_from_llm": data.get("suggestions", []),
            }

        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text as condition
            return {
                "status": "unknown",
                "condition": response_text[:200] if response_text else "Could not parse response",
                "confidence": 0.5,
                "all_predictions": [],
            }
        except Exception as e:
            return {
                "status": "error",
                "condition": f"Analysis failed: {str(e)}",
                "confidence": 0.0,
                "all_predictions": [],
            }
