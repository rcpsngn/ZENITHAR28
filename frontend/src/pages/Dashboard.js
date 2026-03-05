import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, FileText, Users, CheckCircle, 
  Banknote, Settings, LogOut, Menu, X 
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { authAPI } from '../lib/api';
import DashboardHome from '../components/dashboard/DashboardHome';
import PersonnelPage from './personnel/PersonnelPage';

const LOGO_URL = 'https://static.prod-images.emergentagent.com/jobs/1fb06072-670b-49e1-9107-e57d39d3aeac/images/48d24952772b007d8f1595c8f786b20ff8832a50d29b7a2c9de063350c241f5c.png';

const Dashboard = ({ user, onLogout }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [subscription, setSubscription] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    authAPI.getSubscription()
      .then(res => setSubscription(res.data))
      .catch(err => console.error(err));
  }, []);

  const menuItems = [
    { icon: LayoutDashboard, label: 'Ana Sayfa', path: '/dashboard' },
    { icon: FileText, label: 'E-Fatura/İrsaliye', path: '/dashboard/invoices' },
    { icon: Users, label: 'Personel', path: '/dashboard/personnel' },
    { icon: CheckCircle, label: 'Çek/Senet', path: '/dashboard/checks' },
    { icon: Banknote, label: 'Cari Hesap', path: '/dashboard/accounts' },
    { icon: Settings, label: 'Ayarlar', path: '/dashboard/settings' },
  ];

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="fixed top-0 w-full bg-white border-b border-slate-200 z-40 h-16">
        <div className="h-full px-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden"
              data-testid="mobile-menu-toggle"
            >
              {sidebarOpen ? <X /> : <Menu />}
            </button>
            <div className="flex items-center gap-3">
              <img src={LOGO_URL} alt="ZENITHAR" className="h-8 w-8" />
              <span className="text-xl font-manrope font-black text-slate-900">ZENITHAR</span>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {subscription && !subscription.is_active && (
              <span className="text-sm text-red-600 font-bold">Aboneliğiniz sona erdi</span>
            )}
            <span className="text-sm text-slate-600 hidden sm:block">{user.username}</span>
            <Button
              onClick={handleLogout}
              variant="ghost"
              size="sm"
              data-testid="logout-btn"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <aside 
        className={`fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-white border-r border-slate-200 z-30 transition-transform lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        data-testid="sidebar"
      >
        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                data-testid={`nav-${item.label.toLowerCase().replace(/[\/\s]/g, '-')}`}
              >
                <div className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-primary text-white' 
                    : 'text-slate-700 hover:bg-slate-100'
                }`}>
                  <item.icon className="h-5 w-5" strokeWidth={1.5} />
                  <span className="font-medium">{item.label}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        {subscription && (
          <div className="absolute bottom-4 left-4 right-4 p-4 bg-emerald-50 rounded-lg border border-emerald-200">
            <p className="text-xs font-bold text-emerald-900 mb-1">
              {subscription.plan === 'trial' ? '7 Günlük Deneme' : 
               subscription.plan === 'monthly' ? 'Aylık Plan' : 'Yıllık Plan'}
            </p>
            <p className="text-xs text-emerald-700">
              {new Date(subscription.end_date).toLocaleDateString('tr-TR')} tarihine kadar
            </p>
          </div>
        )}
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
            <Route path="/invoices" element={<div className="text-center p-12"><h2 className="text-2xl font-bold">E-Fatura/İrsaliye modülü yakında...</h2></div>} />
            <Route path="/personnel/*" element={<PersonnelPage />} />
            <Route path="/checks" element={<div className="text-center p-12"><h2 className="text-2xl font-bold">Çek/Senet modülü yakında...</h2></div>} />
            <Route path="/accounts" element={<div className="text-center p-12"><h2 className="text-2xl font-bold">Cari Hesap modülü yakında...</h2></div>} />
            <Route path="/settings" element={<div className="text-center p-12"><h2 className="text-2xl font-bold">Ayarlar modülü yakında...</h2></div>} />
          </Routes>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
