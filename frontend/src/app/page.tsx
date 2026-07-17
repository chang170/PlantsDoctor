"use client";

import { useState, useRef, useEffect } from "react";
import InstallPrompt from "./install-prompt";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://plantsdoctor-uhrl.onrender.com";

interface PlantResult {
  plant_name: string;
  scientific_name: string;
  other_common_names: string[];
  origin: string;
  category: string;
  confidence: number;
  all_predictions: { name: string; confidence: number }[];
}

interface HealthResult {
  status: string;
  condition: string;
  confidence: number;
  all_predictions: { condition: string; confidence: number }[];
}

interface Details {
  watering: string;
  sunlight: string;
  soil_type: string;
  toxicity: string;
  growth_rate: string;
  mature_size: string;
  season: string;
  difficulty: string;
  fun_fact: string;
  ripeness: string | null;
  edibility: string | null;
  nutrition: string | null;
  storage_tips: string | null;
}

interface Suggestions {
  issue: string;
  suggestions: string[];
}

interface AnalysisResult {
  plant: PlantResult;
  health: HealthResult;
  details: Details;
  suggestions: Suggestions;
}

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

export default function Home() {
  const [image, setImage] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Block browser back button
  useEffect(() => {
    window.history.pushState(null, "", window.location.href);
    const handlePopState = () => {
      window.history.pushState(null, "", window.location.href);
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setImage(URL.createObjectURL(selected));
      setResult(null);
      setError(null);
      setChatMessages([]);
    }
  };

  const compressImage = (file: File): Promise<File> => {
    return new Promise((resolve) => {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d")!;
      const img = new Image();
      img.onload = () => {
        const maxSize = 1024;
        let { width, height } = img;
        if (width > maxSize || height > maxSize) {
          if (width > height) {
            height = (height / width) * maxSize;
            width = maxSize;
          } else {
            width = (width / height) * maxSize;
            height = maxSize;
          }
        }
        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(img, 0, 0, width, height);
        canvas.toBlob(
          (blob) => {
            resolve(new File([blob!], file.name, { type: "image/jpeg" }));
          },
          "image/jpeg",
          0.8
        );
      };
      img.src = URL.createObjectURL(file);
    });
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    try {
      const compressed = await compressImage(file);
      const formData = new FormData();
      formData.append("file", compressed);

      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
        signal: AbortSignal.timeout(120000),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`HTTP ${response.status}: ${text}`);
      }
      const data: AnalysisResult = await response.json();
      setResult(data);
    } catch (err) {
      if (err instanceof Error && err.name === "TimeoutError") {
        setError("Request timed out. Please try again.");
      } else if (err instanceof Error) {
        setError(`Failed: ${err.message}`);
      } else {
        setError("Failed to analyze image. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFollowUp = async () => {
    if (!chatInput.trim() || !file || !result) return;
    const question = chatInput.trim();
    setChatInput("");
    setChatMessages((prev) => [...prev, { role: "user", text: question }]);
    setChatLoading(true);

    try {
      const compressed = await compressImage(file);
      const formData = new FormData();
      formData.append("file", compressed);
      formData.append("question", question);
      formData.append("context", JSON.stringify(result));

      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        body: formData,
        signal: AbortSignal.timeout(60000),
      });

      if (!response.ok) {
        throw new Error("Failed to get answer");
      }
      const data = await response.json();
      setChatMessages((prev) => [...prev, { role: "assistant", text: data.answer }]);
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Sorry, I couldn't answer that. Please try again." },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleReset = () => {
    setImage(null);
    setFile(null);
    setResult(null);
    setError(null);
    setChatMessages([]);
    setChatInput("");
  };

  return (
    <div className="container">
      <header className="header">
        <h1>🌿 Plant Health AI</h1>
        <p>Identify plants, fruits, and vegetables — get health info and care tips</p>
      </header>

      <InstallPrompt />

      {!image && (
        <div className="upload-buttons">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            aria-label="Upload plant image from gallery"
            style={{ display: "none" }}
          />
          <input
            id="camera-input"
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleImageSelect}
            aria-label="Take a photo"
            style={{ display: "none" }}
          />
          <button
            className="btn btn-primary"
            onClick={() => fileInputRef.current?.click()}
            style={{ marginBottom: "0.75rem" }}
          >
            🖼️ Choose from Gallery
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => document.getElementById("camera-input")?.click()}
          >
            📸 Take a Photo
          </button>
        </div>
      )}

      {image && (
        <>
          <img src={image} alt="Selected plant" className="preview-image" />
          {!result && (
            <button
              className="btn btn-primary"
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? "Analyzing... (this may take a moment)" : "Analyze"}
            </button>
          )}
        </>
      )}

      {error && <p style={{ color: "#dc2626", marginTop: "1rem", fontSize: "0.875rem" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: "1.5rem" }}>
          <PlantCard plant={result.plant} />
          <HealthCard health={result.health} />
          <DetailsCard details={result.details} category={result.plant.category} />
          <SuggestionsCard suggestions={result.suggestions} />

          {/* Follow-up Chat */}
          <div className="card" style={{ marginTop: "1rem" }}>
            <h3 className="card-title">💬 Ask a Follow-up Question</h3>
            {chatMessages.map((msg, i) => (
              <div
                key={i}
                style={{
                  marginTop: "0.5rem",
                  padding: "0.5rem 0.75rem",
                  borderRadius: "0.5rem",
                  background: msg.role === "user" ? "#dcfce7" : "#f3f4f6",
                  textAlign: msg.role === "user" ? "right" : "left",
                  fontSize: "0.875rem",
                }}
              >
                {msg.text}
              </div>
            ))}
            {chatLoading && (
              <p style={{ fontSize: "0.8rem", color: "#888", marginTop: "0.5rem" }}>Thinking...</p>
            )}
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleFollowUp()}
                placeholder="e.g., Is this toxic to cats?"
                style={{
                  flex: 1,
                  padding: "0.625rem",
                  borderRadius: "0.5rem",
                  border: "1px solid #d1d5db",
                  fontSize: "0.875rem",
                }}
                disabled={chatLoading}
                aria-label="Ask a follow-up question"
              />
              <button
                className="btn btn-primary"
                onClick={handleFollowUp}
                disabled={chatLoading || !chatInput.trim()}
                style={{ width: "auto", padding: "0.625rem 1rem" }}
              >
                Ask
              </button>
            </div>
          </div>
        </div>
      )}

      {image && (
        <button className="btn btn-primary" onClick={handleReset} style={{ marginTop: "0.75rem" }}>
          🔄 Analyze Another Plant
        </button>
      )}
    </div>
  );
}

function PlantCard({ plant }: { plant: PlantResult }) {
  return (
    <div className="card">
      <h3 className="card-title">🌱 Identified</h3>
      <p className="card-value">{plant.plant_name}</p>
      {plant.scientific_name && (
        <p className="card-subtitle"><em>{plant.scientific_name}</em></p>
      )}
      {plant.category && (
        <p className="card-detail"><strong>Type:</strong> {plant.category}</p>
      )}
      {plant.origin && (
        <p className="card-detail"><strong>Origin:</strong> {plant.origin}</p>
      )}
      {plant.other_common_names && plant.other_common_names.length > 0 && (
        <p className="card-detail"><strong>Also known as:</strong> {plant.other_common_names.join(", ")}</p>
      )}
      <p className="card-confidence">Confidence: {Math.round(plant.confidence * 100)}%</p>
    </div>
  );
}

function HealthCard({ health }: { health: HealthResult }) {
  const icon = health.status === "healthy" ? "✅" : "⚠️";
  return (
    <div className="card">
      <h3 className="card-title">{icon} Health Status</h3>
      <p className="card-value">{health.condition}</p>
      <p className="card-confidence">Confidence: {Math.round(health.confidence * 100)}%</p>
    </div>
  );
}

function DetailsCard({ details, category }: { details: Details; category: string }) {
  const isFruitOrVeg = category === "fruit" || category === "vegetable";

  return (
    <div className="card">
      <h3 className="card-title">📋 Details</h3>
      {details.watering && <p className="card-detail"><strong>💧 Watering:</strong> {details.watering}</p>}
      {details.sunlight && <p className="card-detail"><strong>☀️ Sunlight:</strong> {details.sunlight}</p>}
      {details.soil_type && <p className="card-detail"><strong>🪴 Soil:</strong> {details.soil_type}</p>}
      {details.toxicity && <p className="card-detail"><strong>⚠️ Toxicity:</strong> {details.toxicity}</p>}
      {details.growth_rate && <p className="card-detail"><strong>📈 Growth rate:</strong> {details.growth_rate}</p>}
      {details.mature_size && <p className="card-detail"><strong>📏 Mature size:</strong> {details.mature_size}</p>}
      {details.season && <p className="card-detail"><strong>🗓️ Season:</strong> {details.season}</p>}
      {details.difficulty && <p className="card-detail"><strong>🎯 Difficulty:</strong> {details.difficulty}</p>}
      {isFruitOrVeg && details.ripeness && <p className="card-detail"><strong>🍎 Ripeness:</strong> {details.ripeness}</p>}
      {isFruitOrVeg && details.edibility && <p className="card-detail"><strong>🍽️ Edibility:</strong> {details.edibility}</p>}
      {isFruitOrVeg && details.nutrition && <p className="card-detail"><strong>💊 Nutrition:</strong> {details.nutrition}</p>}
      {isFruitOrVeg && details.storage_tips && <p className="card-detail"><strong>🧊 Storage:</strong> {details.storage_tips}</p>}
      {details.fun_fact && <p className="card-detail"><strong>💡 Fun fact:</strong> {details.fun_fact}</p>}
    </div>
  );
}

function SuggestionsCard({ suggestions }: { suggestions: Suggestions }) {
  return (
    <div className="card">
      <h3 className="card-title">💡 Care Suggestions</h3>
      <p style={{ fontWeight: 600, marginTop: "0.25rem" }}>{suggestions.issue}</p>
      <ul style={{ marginTop: "0.5rem", paddingLeft: "1.25rem" }}>
        {suggestions.suggestions.map((s, i) => (
          <li key={i} style={{ marginBottom: "0.25rem", fontSize: "0.9rem" }}>{s}</li>
        ))}
      </ul>
    </div>
  );
}
