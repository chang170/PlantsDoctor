"use client";

import { useState, useEffect } from "react";

export default function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<Event | null>(null);
  const [showInstall, setShowInstall] = useState(false);
  const [isIOS, setIsIOS] = useState(false);

  useEffect(() => {
    // Detect iOS
    const ios = /iphone|ipad|ipod/.test(navigator.userAgent.toLowerCase());
    const standalone = (window.navigator as any).standalone;
    if (ios && !standalone) {
      setIsIOS(true);
      setShowInstall(true);
    }

    // Android / Chrome install prompt
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstall(true);
    };
    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  const handleInstall = async () => {
    if (deferredPrompt) {
      (deferredPrompt as any).prompt();
      const result = await (deferredPrompt as any).userChoice;
      if (result.outcome === "accepted") {
        setShowInstall(false);
      }
      setDeferredPrompt(null);
    }
  };

  if (!showInstall) return null;

  return (
    <div style={{
      background: "#dcfce7",
      border: "1px solid #86efac",
      borderRadius: "0.75rem",
      padding: "1rem",
      margin: "1rem 0",
      textAlign: "center",
    }}>
      {isIOS ? (
        <p style={{ fontSize: "0.875rem" }}>
          Install this app: tap <strong>Share</strong> then{" "}
          <strong>Add to Home Screen</strong>
        </p>
      ) : (
        <>
          <p style={{ fontSize: "0.875rem", marginBottom: "0.5rem" }}>
            Install this app for quick access
          </p>
          <button className="btn btn-primary" onClick={handleInstall}>
            Install App
          </button>
        </>
      )}
    </div>
  );
}
