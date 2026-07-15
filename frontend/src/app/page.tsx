"use client";

import { useState, useRef } from "react";
import InstallPrompt from "./install-prompt";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface PlantResult {
  plant_name: string;
  confidence: number;
  all_predictions: { name: string; confidence: number }[];
}

interface HealthResult {
  status: string;
  condition: string;
  confidence: number;
  all_predictions: { condition: string; confidence: number }[];
}

interface Suggestions {
  issue: string;
  suggestions: string[];
}

interface AnalysisResult {
  plant: PlantResult;
  health: HealthResult;
  suggestions: Suggestions;
}

export default function Home() {
  const [image, setImage] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setImage(URL.createObjectURL(selected));
      setResult(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Analysis failed");
      const data: AnalysisResult = await response.json();
      setResult(data);
    } catch (err) {
      setError("Failed to analyze image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setImage(null);
    setFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="container">
      <header className="header">
        <h1>🌿 Plant Health AI</h1>
        <p>Take a photo of your plant to identify it and check its health</p>
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
              {loading ? "Analyzing..." : "Analyze Plant"}
            </button>
          )}
        </>
      )}

      {error && <p style={{ color: "#dc2626", marginTop: "1rem" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: "1.5rem" }}>
          <ResultCard
            title="🌱 Plant Identified"
            value={result.plant.plant_name}
            confidence={result.plant.confidence}
          />
          <ResultCard
            title={result.health.status === "healthy" ? "✅ Health Status" : "⚠️ Health Status"}
            value={result.health.condition}
            confidence={result.health.confidence}
          />
          <SuggestionsCard suggestions={result.suggestions} />
        </div>
      )}

      {image && (
        <button className="btn btn-secondary" onClick={handleReset}>
          Analyze Another Plant
        </button>
      )}
    </div>
  );
}

function ResultCard({ title, value, confidence }: { title: string; value: string; confidence: number }) {
  return (
    <div style={{
      background: "white",
      borderRadius: "0.75rem",
      padding: "1rem",
      marginBottom: "0.75rem",
      boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
    }}>
      <h3 style={{ fontSize: "0.875rem", color: "#666" }}>{title}</h3>
      <p style={{ fontSize: "1.125rem", fontWeight: 600, marginTop: "0.25rem" }}>{value}</p>
      <p style={{ fontSize: "0.75rem", color: "#999", marginTop: "0.25rem" }}>
        Confidence: {Math.round(confidence * 100)}%
      </p>
    </div>
  );
}

function SuggestionsCard({ suggestions }: { suggestions: Suggestions }) {
  return (
    <div style={{
      background: "white",
      borderRadius: "0.75rem",
      padding: "1rem",
      marginBottom: "0.75rem",
      boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
    }}>
      <h3 style={{ fontSize: "0.875rem", color: "#666" }}>💡 Care Suggestions</h3>
      <p style={{ fontWeight: 600, marginTop: "0.25rem" }}>{suggestions.issue}</p>
      <ul style={{ marginTop: "0.5rem", paddingLeft: "1.25rem" }}>
        {suggestions.suggestions.map((s, i) => (
          <li key={i} style={{ marginBottom: "0.25rem", fontSize: "0.9rem" }}>{s}</li>
        ))}
      </ul>
    </div>
  );
}
