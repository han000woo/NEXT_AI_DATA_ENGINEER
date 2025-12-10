// src/components/DigitCanvas.tsx
import React, { useRef, useState, useEffect } from "react";
import { fetchPrediction } from "../api/predictionApi";
import "../App.css"; // 스타일 파일 임포트

interface DigitCanvasProps {
    id: number;
    value: number | string;
    onPredict: (id: number, prediction: number) => void;
    onDelete: (id: number) => void;
    isRemovable: boolean;
}

const DigitCanvas: React.FC<DigitCanvasProps> = ({
    id,
    value,
    onPredict,
    onDelete,
    isRemovable,
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const [loading, setLoading] = useState(false);

    // 초기화
    useEffect(() => {
        clearCanvasUI();
    }, []);

    const clearCanvasUI = () => {
        const canvas = canvasRef.current;
        const ctx = canvas?.getContext("2d");
        if (ctx && canvas) {
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
    };

    const startDrawing = (e: React.MouseEvent) => {
        const canvas = canvasRef.current;
        const ctx = canvas?.getContext("2d");
        if (!ctx || !canvas) return;

        ctx.lineWidth = 15;
        ctx.lineCap = "round";
        ctx.strokeStyle = "black";
        ctx.beginPath();

        const rect = canvas.getBoundingClientRect();
        ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
        setIsDrawing(true);
    };

    const draw = (e: React.MouseEvent) => {
        if (!isDrawing) return;
        const canvas = canvasRef.current;
        const ctx = canvas?.getContext("2d");
        if (ctx && canvas) {
            const rect = canvas.getBoundingClientRect();
            ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
            ctx.stroke();
        }
    };

    const stopDrawing = async () => {
        if (!isDrawing) return;
        setIsDrawing(false);

        // 그림을 다 그리면 자동으로 예측 요청
        const canvas = canvasRef.current;
        if (canvas) {
            setLoading(true);
            const dataURL = canvas.toDataURL("image/png");
            const prediction = await fetchPrediction(dataURL);

            if (prediction !== null) {
                onPredict(id, prediction);
            }
            setLoading(false);
        }
    };

    const handleClear = () => {
        clearCanvasUI();
        onPredict(id, 0); // 값 0으로 초기화
    };

    return (
        <div className="digit-box-container">
            <div className="canvas-wrapper">
                <canvas
                    ref={canvasRef}
                    width={150}
                    height={150}
                    className="digit-canvas"
                    onMouseDown={startDrawing}
                    onMouseMove={draw}
                    onMouseUp={stopDrawing}
                    onMouseLeave={stopDrawing}
                />
                <div className="canvas-controls">
                    <button onClick={handleClear} className="mini-btn">↺</button>
                    {isRemovable && (
                        <button onClick={() => onDelete(id)} className="mini-btn btn-delete">×</button>
                    )}
                </div>
            </div>
            <div className="prediction-box">
                {loading ? "..." : (value !== "" ? value : "?")}
            </div>
        </div>
    );
};

export default DigitCanvas;