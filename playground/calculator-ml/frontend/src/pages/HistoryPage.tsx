const HistoryPage = () => {
    return (
        <div className="page-container">
            <h2 className="page-title">계산 기록</h2>
            <div className="history-list">
                <div className="history-item">
                    <span>12 + 5 = </span> <strong>17</strong>
                    <span className="date">2025.05.10 14:00</span>
                </div>
                <div className="history-item">
                    <span>7 × 3 = </span> <strong>21</strong>
                    <span className="date">2025.05.10 14:05</span>
                </div>
                <p style={{ color: "#888", marginTop: 20 }}>
                    * 추후 DB 연동 예정 기능입니다.
                </p>
            </div>
        </div>
    );
};

export default HistoryPage;