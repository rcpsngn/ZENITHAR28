import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card } from '../components/ui/card';
import { Banknote } from 'lucide-react';
import { toast } from 'sonner';
import { authAPI } from '../lib/api';

const AuthPage = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    company_name: '',
  });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        const response = await authAPI.login({
          username: formData.username,
          password: formData.password,
        });
        toast.success('Başarıyla giriş yaptınız!');
        onLogin(response.data.user, response.data.tokens.access);
        navigate('/dashboard');
      } else {
        if (formData.password !== formData.password_confirm) {
          toast.error('Şifreler eşleşmiyor!');
          setLoading(false);
          return;
        }
        const response = await authAPI.register(formData);
        toast.success('Hesabınız oluşturuldu! 7 günlük deneme süreniz başladı.');
        onLogin(response.data.user, response.data.tokens.access);
        navigate('/dashboard');
      }
    } catch (error) {
      const message = error.response?.data?.detail || 'Bir hata oluştu';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-tr from-emerald-50 to-orange-50 p-4">
      <Card className="w-full max-w-md p-8" data-testid="auth-card">
        <div className="flex items-center justify-center gap-2 mb-8">
          <Banknote className="h-10 w-10 text-primary" />
          <span className="text-3xl font-manrope font-black text-slate-900">MuhasebePro</span>
        </div>

        <h2 className="text-2xl font-manrope font-bold text-center mb-6">
          {isLogin ? 'Giriş Yap' : 'Hesap Oluştur'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="username">Kullanıcı Adı</Label>
            <Input
              id="username"
              data-testid="input-username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
            />
          </div>

          {!isLogin && (
            <>
              <div>
                <Label htmlFor="email">E-posta</Label>
                <Input
                  id="email"
                  type="email"
                  data-testid="input-email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="company">Firma Adı</Label>
                <Input
                  id="company"
                  data-testid="input-company"
                  value={formData.company_name}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                />
              </div>
            </>
          )}

          <div>
            <Label htmlFor="password">Şifre</Label>
            <Input
              id="password"
              type="password"
              data-testid="input-password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />
          </div>

          {!isLogin && (
            <div>
              <Label htmlFor="password_confirm">Şifre Tekrar</Label>
              <Input
                id="password_confirm"
                type="password"
                data-testid="input-password-confirm"
                value={formData.password_confirm}
                onChange={(e) => setFormData({ ...formData, password_confirm: e.target.value })}
                required
              />
            </div>
          )}

          <Button
            type="submit"
            data-testid="auth-submit-btn"
            className="w-full bg-primary hover:bg-primary-hover text-white font-bold"
            disabled={loading}
          >
            {loading ? 'Yükleniyor...' : isLogin ? 'Giriş Yap' : 'Hesap Oluştur'}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <button
            data-testid="toggle-auth-mode"
            onClick={() => setIsLogin(!isLogin)}
            className="text-primary hover:underline"
          >
            {isLogin ? 'Hesabınız yok mu? Kayıt olun' : 'Zaten hesabınız var mı? Giriş yapın'}
          </button>
        </div>
      </Card>
    </div>
  );
};

export default AuthPage;
