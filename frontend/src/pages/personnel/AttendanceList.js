import React, { useState, useEffect } from 'react';
import { Calendar, Clock } from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { personnelAPI } from '../../lib/api';
import { toast } from 'sonner';

const AttendanceList = () => {
  const [attendance, setAttendance] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [attRes, empRes] = await Promise.all([
        personnelAPI.getAttendance(),
        personnelAPI.getEmployees({ is_active: true })
      ]);
      setAttendance(attRes.data);
      setEmployees(empRes.data);
    } catch (error) {
      toast.error('Veriler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickEntry = async (employeeId, type) => {
    try {
      await personnelAPI.quickEntry({ employee: employeeId, type });
      toast.success('Kayıt eklendi');
      fetchData();
    } catch (error) {
      toast.error('Kayıt eklenemedi');
    }
  };

  return (
    <div>
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-bold mb-4">Hızlı Giriş/Çıkış</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {employees.slice(0, 8).map((emp) => (
            <div key={emp.id} className="border rounded-lg p-4">
              <p className="font-medium text-sm mb-2">{emp.full_name}</p>
              <div className="flex gap-2">
                <Button size="sm" className="flex-1 bg-green-600 hover:bg-green-700" onClick={() => handleQuickEntry(emp.id, 'entry')}>Giriş</Button>
                <Button size="sm" className="flex-1 bg-red-600 hover:bg-red-700" onClick={() => handleQuickEntry(emp.id, 'exit')}>Çıkış</Button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <h3 className="text-lg font-bold mb-4">Son Kayıtlar</h3>
      {loading ? (
        <div className="text-center py-12">Yükleniyor...</div>
      ) : attendance.length === 0 ? (
        <Card className="p-12 text-center"><p className="text-slate-600">Henüz kayıt yok</p></Card>
      ) : (
        <div className="space-y-2">
          {attendance.slice(0, 20).map((att) => (
            <Card key={att.id} className="p-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium">{att.employee_name}</p>
                  <p className="text-sm text-slate-600">{att.type === 'entry' ? 'Giriş' : 'Çıkış'}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">{new Date(att.date).toLocaleDateString('tr-TR')}</p>
                  <p className="text-sm text-slate-600">{att.time}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default AttendanceList;
