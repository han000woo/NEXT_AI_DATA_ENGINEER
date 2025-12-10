import { Link, useLocation } from "react-router-dom";

const Sidebar = () => {
    const location = useLocation();

    // 현재 경로와 일치하면 active 클래스 부여
    const getClass = (path: string) =>
        location.pathname === path ? "nav-item active" : "nav-item";

    return (
        <nav className="app-sidebar">
            <ul className="nav-list">
                <li>
                    <Link to="/" className={getClass("/")}>
                        🧮 계산기
                    </Link>
                </li>
                <li>
                    <Link to="/history" className={getClass("/history")}>
                        📜 계산 기록
                    </Link>
                </li>
                <li>
                    <Link to="/settings" className={getClass("/settings")}>
                        ⚙️ 설정 (준비중)
                    </Link>
                </li>
            </ul>
        </nav>
    );
};

export default Sidebar;