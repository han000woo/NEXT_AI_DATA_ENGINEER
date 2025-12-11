import { useState } from 'react';
import axios from 'axios';
import './App.css'; // 기본 스타일

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // 1. 파일 선택 시 실행
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file)); // 미리보기 URL 생성
      setResult(null); // 이전 결과 초기화
    }
  };

  // 2. 서버로 전송 (FastAPI와 통신)
  const handleUpload = async () => {
    if (!selectedFile) return alert("사진을 먼저 선택해주세요!");

    const formData = new FormData();
    formData.append("file", selectedFile);

    setLoading(true);
    try {
      // FastAPI 주소로 POST 요청
      const response = await axios.post("http://localhost:8000/predict", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(response.data); // 결과 저장
    } catch (error) {
      console.error("에러 발생:", error);
      alert("서버 연결에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "50px", textAlign: "center", fontFamily: "sans-serif" }}>
      <h1>🐶 개 vs 고양이 판독기 🐱</h1>

      {/* 이미지 업로드 영역 */}
      <div style={{ margin: "20px 0" }}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
      </div>

      {/* 미리보기 이미지 */}
      {preview && (
        <div>
          <img
            src={preview}
            alt="Preview"
            style={{ width: "300px", borderRadius: "10px", objectFit: "cover" }}
          />
        </div>
      )}

      {/* 판독 버튼 */}
      <button
        onClick={handleUpload}
        disabled={loading}
        style={{ marginTop: "20px", padding: "10px 20px", fontSize: "16px", cursor: "pointer" }}
      >
        {loading ? "판독 중..." : "결과 확인하기"}
      </button>

      {/* 결과 표시 */}
      {result && (
        <div style={{ marginTop: "30px", padding: "20px", border: "2px solid #ddd", borderRadius: "10px" }}>
          <h2 style={{ color: result.result === 'dog' ? 'blue' : 'orange' }}>
            {result.message}
          </h2>
          <p>확신도: <strong>{result.confidence}%</strong></p>
        </div>
      )}
    </div>
  );
}

export default App;