import React from 'react';
import { Card } from '../ui/card';
import { FileText, Users, CheckCircle, Banknote, TrendingUp, AlertCircle } from 'lucide-react';

const DashboardHome = ({ user }) => {
  const stats = [
    { icon: FileText, label: 'Toplam Fatura', value: '0', color: 'text-blue-600', bg: 'bg-blue-50' },
    { icon: Users, label: 'Aktif Personel', value: '0', color: 'text-green-600', bg: 'bg-green-50' },
    { icon: CheckCircle, label: 'Bekleyen Çek', value: '0', color: 'text-orange-600', bg: 'bg-orange-50' },
    { icon: Banknote, label: 'Cari Bakiye', value: '₺0', color: 'text-purple-600', bg: 'bg-purple-50' },
  ];

  return (
    <div data-testid="dashboard-home">
      <div className="mb-8">
        <h1 className="text-3xl font-manrope font-bold text-slate-900 mb-2">
          Hoş Geldiniz, {user.username}!
        </h1>
        <p className="text-slate-600">
          Muhasebe verilerinize hızlıca göz atın
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, idx) => (
          <Card key={idx} className="p-6 hover:shadow-md transition-shadow" data-testid={`stat-${stat.label.toLowerCase().replace(/\s/g, '-')}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">{stat.label}</p>
                <p className="text-3xl font-black text-slate-900">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-lg ${stat.bg}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} strokeWidth={1.5} />
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="h-5 w-5 text-primary" />
            <h3 className="text-xl font-manrope font-bold">Son İşlemler</h3>
          </div>
          <p className="text-slate-600 text-center py-8">
            Henüz işlem bulunmuyor
          </p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="h-5 w-5 text-orange-600" />
            <h3 className="text-xl font-manrope font-bold">Hatırlatmalar</h3>
          </div>
          <p className="text-slate-600 text-center py-8">
            Henüz hatırlatma bulunmuyor
          </p>
        </Card>
      </div>

      <div className="mt-8 p-6 bg-gradient-to-br from-emerald-50 to-orange-50 rounded-xl border border-emerald-200">
        <h3 className="text-xl font-manrope font-bold mb-2 text-slate-900">
          Başlamak için ipuçları
        </h3>
        <ul className="space-y-2 text-slate-700">
          <li>• Sol menüden E-Fatura/İrsaliye bölümüne giderek ilk faturanızı oluşturun</li>
          <li>• Personel bölümünden çalışanlarınızı sisteme ekleyin</li>
          <li>• Cari Hesap bölümünden müşteri ve tedarikçilerinizi tanımlayın</li>
          <li>• KDV işlemleri için rehberlik almak istiyorsanız ilgili modüle göz atın</li>
        </ul>
      </div>
    </div>
  );
};

export default DashboardHome;
