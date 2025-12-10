import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "./layout/MainLayout";
import CalculatorPage from "./pages/CalculatorPage";
import HistoryPage from "./pages/HistoryPage";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* MainLayout을 부모로 감싸서 모든 페이지에 헤더/푸터 적용 */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<CalculatorPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="settings" element={<div className="page-container">설정 페이지</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;