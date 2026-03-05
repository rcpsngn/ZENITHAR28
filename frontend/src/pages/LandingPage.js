import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Users, CheckCircle, PieChart, Shield } from 'lucide-react';
import { Button } from '../components/ui/button';

const LOGO_URL = 'https://static.prod-images.emergentagent.com/jobs/1fb06072-670b-49e1-9107-e57d39d3aeac/images/48d24952772b007d8f1595c8f786b20ff8832a50d29b7a2c9de063350c241f5c.png';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-white">
      <nav className="fixed top-0 w-full bg-white/70 backdrop-blur-xl border-b border-slate-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <img src={LOGO_URL} alt="ZENITHAR" className="h-10 w-10" />
              <span className="text-2xl font-manrope font-black text-slate-900">ZENITHAR</span>
            </div>
            <Link to="/auth">
              <Button data-testid="nav-login-btn" className="bg-primary hover:bg-primary-hover text-white font-bold">
                Giriş Yap
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-tr from-emerald-50 to-orange-50">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl md:text-7xl font-manrope font-black tracking-tighter text-slate-900 mb-6">
                Muhasebenizi <span className="text-primary">Yönetin</span>
              </h1>
              <p className="text-lg text-slate-600 mb-8 leading-relaxed">
                E-Fatura, personel takibi, çek-senet yönetimi. Güçlü, hızlı ve profesyonel muhasebe çözümü.
              </p>
              <div className="flex gap-4">
                <Link to="/auth">
                  <Button data-testid="hero-cta-btn" size="lg" className="bg-secondary hover:bg-secondary-hover text-white font-bold text-lg px-8 py-6 rounded-lg shadow-lg">
                    7 Gün Ücretsiz Deneyin
                  </Button>
                </Link>
              </div>
            </div>
            <div className="relative">
              <img 
                src="https://images.unsplash.com/photo-1770681381576-fe1ca0178da1?crop=entropy&cs=srgb&fm=jpg&q=85" 
                alt="Profesyonel çalışma alanı"
                className="rounded-xl shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-manrope font-black text-center mb-16 text-slate-900">
            Tüm İhtiyaçlarınız Tek Platformda
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: FileText, title: 'E-Fatura & E-İrsaliye', desc: 'Faturalarınızı kolayca yönetin ve takip edin' },
              { icon: Users, title: 'Personel Yönetimi', desc: 'Giriş-çıkış, maaş ve izin takibi' },
              { icon: CheckCircle, title: 'Çek & Senet Takibi', desc: 'Alınan ve verilen çek/senetleri yönetin' },
              { icon: PieChart, title: 'Cari Hesap', desc: 'Müşteri ve tedarikçi bakiyelerini kontrol edin' },
              { icon: Shield, title: 'KDV İşlemleri', desc: 'İade ve mahsup işlemlerinde rehberlik' },
              { icon: FileText, title: 'Detaylı Raporlar', desc: 'Finansal raporlar ve analizler' },
            ].map((feature, idx) => (
              <div 
                key={idx}
                className="p-8 rounded-xl border border-slate-200 bg-white hover:shadow-md transition-shadow"
              >
                <feature.icon className="h-12 w-12 text-primary mb-4" strokeWidth={1.5} />
                <h3 className="text-xl font-manrope font-bold mb-2 text-slate-900">{feature.title}</h3>
                <p className="text-slate-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-50">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-4xl font-manrope font-black mb-6 text-slate-900">Fiyatlandırma</h2>
          <p className="text-lg text-slate-600 mb-12">7 gün ücretsiz deneyin, sonra size uygun planı seçin</p>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
            <div className="p-8 rounded-2xl border-2 border-slate-200 bg-white">
              <h3 className="text-2xl font-manrope font-bold mb-2">Aylık</h3>
              <p className="text-4xl font-black text-primary mb-6">₺299<span className="text-lg text-slate-600">/ay</span></p>
              <ul className="space-y-3 text-left mb-8">
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-primary" />
                  <span>Tüm özellikler</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-primary" />
                  <span>Sınırsız kullanıcı</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-primary" />
                  <span>Öncelikli destek</span>
                </li>
              </ul>
              <Link to="/auth">
                <Button data-testid="pricing-monthly-btn" className="w-full bg-primary hover:bg-primary-hover text-white font-bold">
                  Başlayın
                </Button>
              </Link>
            </div>
            
            <div className="p-8 rounded-2xl border-2 border-primary bg-gradient-to-br from-white to-emerald-50 relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-secondary text-white px-4 py-1 rounded-full text-sm font-bold">
                En Popüler
              </div>
              <h3 className="text-2xl font-manrope font-bold mb-2">Yıllık</h3>
              <p className="text-4xl font-black text-primary mb-6">₺2.999<span className="text-lg text-slate-600">/yıl</span></p>
              <p className="text-sm text-secondary font-bold mb-6">2 ay bedava!</p>
              <ul className="space-y-3 text-left mb-8">
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-primary" />
                  <span>Tüm özellikler</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-primary" />
                  <span>Sınırsız kullanıcı</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-primary" />
                  <span>Öncelikli destek</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-primary" />
                  <span>%17 tasarruf</span>
                </li>
              </ul>
              <Link to="/auth">
                <Button data-testid="pricing-yearly-btn" className="w-full bg-secondary hover:bg-secondary-hover text-white font-bold">
                  Başlayın
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="py-12 px-4 sm:px-6 lg:px-8 bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <img src={LOGO_URL} alt="ZENITHAR" className="h-8 w-8" />
            <span className="text-2xl font-manrope font-black">ZENITHAR</span>
          </div>
          <p className="text-slate-400">© 2026 ZENITHAR. Tüm hakları saklıdır.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
