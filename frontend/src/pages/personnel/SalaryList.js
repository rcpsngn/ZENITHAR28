import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { personnelAPI } from '../../lib/api';
import { toast } from 'sonner';
import { CheckCircle } from 'lucide-react';

const SalaryList = () => {
  const [salaries, setSalaries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSalaries();
  }, []);

  const fetchSalaries = async () => {
    try {
      const response = await personnelAPI.getSalaries();
      setSalaries(response.data);
    } catch (error) {
      toast.error('Maaşlar yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkPaid = async (id) => {
    try {
      await personnelAPI.markPaid(id);
      toast.success('Ödendi olarak işaretlendi');
      fetchSalaries();
    } catch (error) {
      toast.error('İşlem başarısız');
    }
  };

  return (
    <div>
      {loading ? (
        <div className="text-center py-12">Yükleniyor...</div>
      ) : salaries.length === 0 ? (
        <Card className="p-12 text-center"><p className="text-slate-600">Henüz maaş kaydı yok</p></Card>
      ) : (
        <div className="grid gap-4">
          {salaries.map((salary) => (
            <Card key={salary.id} className="p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-lg mb-2">{salary.employee_name}</h3>
                  <p className="text-slate-600 mb-4">{salary.month_name} {salary.year}</p>
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div><p className="text-slate-500">Temel</p><p className="font-medium">₺{Number(salary.base_salary).toLocaleString('tr-TR')}</p></div>
                    <div><p className="text-slate-500">Prim</p><p className="font-medium text-green-600">+₺{Number(salary.bonus).toLocaleString('tr-TR')}</p></div>
                    <div><p className="text-slate-500">Kesinti</p><p className="font-medium text-red-600">-₺{Number(salary.deductions).toLocaleString('tr-TR')}</p></div>
                    <div><p className="text-slate-500">Net</p><p className="font-bold text-lg">₺{Number(salary.net_salary).toLocaleString('tr-TR')}</p></div>
                  </div>
                </div>
                <div className="text-right">
                  {salary.status === 'paid' ? (
                    <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">Ödendi</span>
                  ) : (
                    <Button size="sm" className="bg-primary hover:bg-primary-hover" onClick={() => handleMarkPaid(salary.id)}>
                      <CheckCircle className="h-4 w-4 mr-2" />Öde
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default SalaryList;
