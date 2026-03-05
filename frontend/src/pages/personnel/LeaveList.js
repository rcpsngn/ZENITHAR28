import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { personnelAPI } from '../../lib/api';
import { toast } from 'sonner';
import { Check, X } from 'lucide-react';

const LeaveList = () => {
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaves();
  }, []);

  const fetchLeaves = async () => {
    try {
      const response = await personnelAPI.getLeaves();
      setLeaves(response.data);
    } catch (error) {
      toast.error('İzinler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      await personnelAPI.approveLeave(id);
      toast.success('İzin onaylandı');
      fetchLeaves();
    } catch (error) {
      toast.error('İşlem başarısız');
    }
  };

  const handleReject = async (id) => {
    try {
      await personnelAPI.rejectLeave(id, 'Reddedildi');
      toast.success('İzin reddedildi');
      fetchLeaves();
    } catch (error) {
      toast.error('İşlem başarısız');
    }
  };

  const getTypeLabel = (type) => {
    const types = { annual: 'Yıllık', sick: 'Hastalık', unpaid: 'Ücretsiz', maternity: 'Doğum', other: 'Diğer' };
    return types[type] || type;
  };

  return (
    <div>
      {loading ? (
        <div className="text-center py-12">Yükleniyor...</div>
      ) : leaves.length === 0 ? (
        <Card className="p-12 text-center"><p className="text-slate-600">Henüz izin talebi yok</p></Card>
      ) : (
        <div className="grid gap-4">
          {leaves.map((leave) => (
            <Card key={leave.id} className="p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-bold text-lg">{leave.employee_name}</h3>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">{getTypeLabel(leave.type)}</span>
                    {leave.status === 'pending' && <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">Bekliyor</span>}
                    {leave.status === 'approved' && <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Onaylandı</span>}
                    {leave.status === 'rejected' && <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">Reddedildi</span>}
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm mb-2">
                    <div><p className="text-slate-500">Başlangıç</p><p className="font-medium">{new Date(leave.start_date).toLocaleDateString('tr-TR')}</p></div>
                    <div><p className="text-slate-500">Bitiş</p><p className="font-medium">{new Date(leave.end_date).toLocaleDateString('tr-TR')}</p></div>
                    <div><p className="text-slate-500">Gün</p><p className="font-medium">{leave.days} gün</p></div>
                  </div>
                  {leave.reason && <p className="text-sm text-slate-600">{leave.reason}</p>}
                </div>
                {leave.status === 'pending' && (
                  <div className="flex gap-2">
                    <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={() => handleApprove(leave.id)}>
                      <Check className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="outline" className="text-red-600 hover:bg-red-50" onClick={() => handleReject(leave.id)}>
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default LeaveList;
