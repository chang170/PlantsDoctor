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

    MODEL = "qwen/qwen3.6-27b"
    FALLBACK_MODEL = "llama-3.3-70b-versatile"

    PROMPT = """You are a plant, tree, fruit, and vegetable expert botanist. Analyze this image and provide detailed information.

If the image shows a fruit or vegetable, include ripeness, edibility, nutrition, and storage info.
If the image shows a plant or tree, include care information.

Respond in this exact JSON format (no markdown, no extra text):
{
  "plant_name": "common name of the plant/fruit/vegetable",
  "scientific_name": "Latin/botanical name",
  "other_common_names": ["other names people call it"],
  "origin": "native region or country of origin",
  "category": "houseplant", "tree", "flower", "fruit", "vegetable", "succulent", "herb", or "other",
  "status": "healthy" or "unhealthy",
  "condition": "brief description of the condition",
  "confidence": 0.0 to 1.0,
  "problems": ["list of problems if any"],
  "suggestions": ["list of care suggestions"],
  "watering": "watering needs description",
  "sunlight": "sunlight requirements",
  "soil_type": "preferred soil type",
  "toxicity": "toxicity info for pets and children",
  "growth_rate": "slow, medium, or fast",
  "mature_size": "expected mature height and spread",
  "season": "blooming, fruiting, or harvest season",
  "difficulty": "easy, moderate, or hard to care for",
  "fun_fact": "an interesting fact about this plant",
  "ripeness": "ripe, unripe, or overripe (for fruits/vegetables only, otherwise null)",
  "edibility": "is it safe to eat, any warnings (for fruits/vegetables only, otherwise null)",
  "nutrition": "key vitamins and minerals (for fruits/vegetables only, otherwise null)",
  "storage_tips": "how to store it (for fruits/vegetables only, otherwise null)"
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

        messages = [
            {
                "role": "system",
                "content": "/no_think"
            },
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
        ]

        try:
            # Try primary model
            try:
                completion = self.client.chat.completions.create(
                    model=self.MODEL,
                    messages=messages,
                    temperature=0.3,
                    max_completion_tokens=4096,
                )
            except Exception:
                completion = self.client.chat.completions.create(
                    model=self.FALLBACK_MODEL,
                    messages=messages,
                    temperature=0.3,
                    max_completion_tokens=4096,
                )

            response_text = completion.choices[0].message.content.strip()

            # Strip thinking tags if present (Qwen model)
            if "<think>" in response_text:
                think_end = response_text.find("</think>")
                if think_end != -1:
                    response_text = response_text[think_end + 8:].strip()
                else:
                    # Thinking never ended — try to extract JSON from response
                    json_start = response_text.find("{")
                    if json_start != -1:
                        response_text = response_text[json_start:]
                    else:
                        # No JSON found at all, return error
                        return {
                            "status": "error",
                            "condition": "Model response was incomplete. Please try again.",
                            "confidence": 0.0,
                            "all_predictions": [],
                        }

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
                "scientific_name": data.get("scientific_name", ""),
                "other_common_names": data.get("other_common_names", []),
                "origin": data.get("origin", ""),
                "category": data.get("category", ""),
                "watering": data.get("watering", ""),
                "sunlight": data.get("sunlight", ""),
                "soil_type": data.get("soil_type", ""),
                "toxicity": data.get("toxicity", ""),
                "growth_rate": data.get("growth_rate", ""),
                "mature_size": data.get("mature_size", ""),
                "season": data.get("season", ""),
                "difficulty": data.get("difficulty", ""),
                "fun_fact": data.get("fun_fact", ""),
                "ripeness": data.get("ripeness"),
                "edibility": data.get("edibility"),
                "nutrition": data.get("nutrition"),
                "storage_tips": data.get("storage_tips"),
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

    def ask_question(self, image: Image.Image, question: str, context: dict) -> str:
        """Answer a follow-up question about an already-analyzed plant."""
        if not self.client:
            return "Unable to answer — GROQ_API_KEY not set."

        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

        context_summary = (
            f"This plant was identified as: {context.get('plant', {}).get('plant_name', 'Unknown')} "
            f"({context.get('plant', {}).get('scientific_name', '')}).\n"
            f"Category: {context.get('plant', {}).get('category', '')}.\n"
            f"Health status: {context.get('health', {}).get('status', 'unknown')} - "
            f"{context.get('health', {}).get('condition', '')}."
        )

        prompt = f"""You previously analyzed this plant image. Here is what you found:

{context_summary}

The user has a follow-up question: "{question}"

Please answer the question based on what you can see in the image and your botanical knowledge. 
Keep the answer concise and helpful (2-4 sentences). Do not use markdown formatting."""

        try:
            completion = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                temperature=0.4,
                max_completion_tokens=512,
            )

            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Sorry, I couldn't answer that: {str(e)}"

    def ask_question_text(self, question: str, context: dict) -> str:
        """Answer a follow-up question using only text context (no image resend)."""
        if not self.client:
            return "Unable to answer — GROQ_API_KEY not set."

        context_summary = (
            f"Plant: {context.get('plant', {}).get('plant_name', 'Unknown')} "
            f"({context.get('plant', {}).get('scientific_name', '')}).\n"
            f"Category: {context.get('plant', {}).get('category', '')}.\n"
            f"Origin: {context.get('plant', {}).get('origin', '')}.\n"
            f"Health: {context.get('health', {}).get('status', 'unknown')} - "
            f"{context.get('health', {}).get('condition', '')}.\n"
            f"Details: watering={context.get('details', {}).get('watering', '')}, "
            f"sunlight={context.get('details', {}).get('sunlight', '')}, "
            f"toxicity={context.get('details', {}).get('toxicity', '')}."
        )

        prompt = f"""You are a plant expert. You previously analyzed a plant and found:

{context_summary}

The user asks: "{question}"

Answer concisely (2-4 sentences) based on your botanical knowledge about this specific plant."""

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.4,
                max_completion_tokens=512,
            )

            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Sorry, I couldn't answer that: {str(e)}"
