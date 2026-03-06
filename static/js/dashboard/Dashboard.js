import React, { useState } from "react";
import { Routes, Route, Link, useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  Users,
  CheckCircle,
  Banknote,
  Settings,
  LogOut,
  Menu,
  X,
} from "lucide-react";

import DashboardHome from "../dashboard/DashboardHome";
import PersonnelPage from "../personnel/PersonnelPage";
import InvoicePage from "../invoices/InvoicePage";

const LOGO_URL =
  "https://static.prod-images.emergentagent.com/jobs/1fb06072-670b-49e1-9107-e57d39d3aeac/images/48d24952772b007d8f1595c8f786b20ff8832a50d29b7a2c9de063350c241f5c.png";

const Dashboard = ({ user, onLogout }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { icon: LayoutDashboard, label: "Ana Sayfa", path: "/dashboard" },
    { icon: FileText, label: "E-Fatura/İrsaliye", path: "/dashboard/invoices" },
    { icon: Users, label: "Personel", path: "/dashboard/personnel" },
    { icon: CheckCircle, label: "Çek/Senet", path: "/dashboard/checks" },
    { icon: Banknote, label: "Cari Hesap", path: "/dashboard/accounts" },
    { icon: Settings, label: "Ayarlar", path: "/dashboard/settings" },
  ];

  const handleLogout = () => {
    onLogout();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-slate-50">

      <div className="fixed top-0 w-full bg-white border-b border-slate-200 z-40 h-16">
        <div className="h-full px-4 flex items-center justify-between">

          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="lg:hidden">
              {sidebarOpen ? <X /> : <Menu />}
            </button>

            <div className="flex items-center gap-3">
              <img src={LOGO_URL} alt="ZENITHAR" className="h-8 w-8" />
              <span className="text-xl font-black text-slate-900">ZENITHAR</span>
            </div>
          </div>

          <div className="flex items-center gap-4">

            <span className="text-sm text-slate-600 hidden sm:block">
              {user?.username}
            </span>

            <button
              onClick={handleLogout}
              className="p-2 rounded hover:bg-slate-100"
            >
              <LogOut className="h-4 w-4" />
            </button>

          </div>
        </div>
      </div>

      <aside
        className={`fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-white border-r border-slate-200 z-30 transition-transform lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <nav className="p-4 space-y-2">

          {menuItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path);

            return (
              <Link key={item.path} to={item.path} onClick={() => setSidebarOpen(false)}>
                <div
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? "bg-primary text-white"
                      : "text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  <item.icon className="h-5 w-5" strokeWidth={1.5} />
                  <span className="font-medium">{item.label}</span>
                </div>
              </Link>
            );
          })}

        </nav>
      </aside>

      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <main className="lg:ml-64 pt-16">
        <div className="p-4 sm:p-6 lg:p-8">

          <Routes>

            <Route path="/" element={<DashboardHome user={user} />} />

            <Route path="/invoices" element={<InvoicePage />} />

            <Route path="/personnel/*" element={<PersonnelPage />} />

            <Route
              path="/checks"
              element={
                <div className="text-center p-12">
                  <h2 className="text-2xl font-bold">
                    Çek/Senet modülü yakında...
                  </h2>
                </div>
              }
            />

            <Route
              path="/accounts"
              element={
                <div className="text-center p-12">
                  <h2 className="text-2xl font-bold">
                    Cari Hesap modülü yakında...
                  </h2>
                </div>
              }
            />

            <Route
              path="/settings"
              element={
                <div className="text-center p-12">
                  <h2 className="text-2xl font-bold">
                    Ayarlar modülü yakında...
                  </h2>
                </div>
              }
            />

          </Routes>

        </div>
      </main>

    </div>
  );
};

export default Dashboard;