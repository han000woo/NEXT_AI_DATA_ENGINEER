
import { Outlet } from "react-router-dom";
import Header from "./Header";
import Sidebar from "./Sidebar";
import Footer from "./Footer";

const MainLayout = () => {
    return (
        <div className="layout-container">
            <Header />
            <div className="layout-body">
                <Sidebar />
                <main className="layout-content">
                    {/* Outlet 자리에 각 페이지 컴포넌트가 렌더링됩니다 */}
                    <Outlet />
                </main>
            </div>
            <Footer />
        </div>
    );
};

export default MainLayout;