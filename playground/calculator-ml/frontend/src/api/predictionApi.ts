// src/api/predictionApi.ts

export const fetchPrediction = async (imageDataUrl: string): Promise<number | null> => {
  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageDataUrl }),
    });

    if (!res.ok) {
      throw new Error("Server response was not ok");
    }

    const json = await res.json();
    return json.prediction; // 백엔드 응답 키값에 맞춰 수정 (예: prediction, result 등)
  } catch (error) {
    console.error("Prediction API Error:", error);
    return null;
  }
};