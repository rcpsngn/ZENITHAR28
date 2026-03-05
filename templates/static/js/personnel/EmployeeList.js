import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, UserCheck, UserX } from 'lucide-react';
import Button from '../../components/ui/button';
import Input from '../../components/ui/input';
import Card from '../../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import Label from '../../components/ui/label';
import { personnelAPI } from '@/services/api';
import { toast } from 'sonner';

const EmployeeList = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    identity_number: '',
    phone: '',
    email: '',
    position: '',
    department: '',
    hire_date: '',
    salary: '',
  });

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await personnelAPI.getEmployees();
      setEmployees(response.data || []);
    } catch (error) {
      console.error('Fetch error:', error);
      toast.error('Personeller yüklenemedi');
      setEmployees([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await personnelAPI.createEmployee(formData);
      toast.success('Personel eklendi');
      setShowDialog(false);
      fetchEmployees();
      setFormData({ full_name: '', identity_number: '', phone: '', email: '', position: '', department: '', hire_date: '', salary: '' });
    } catch (error) {
      toast.error('Personel eklenemedi');
    }
  };

  const handleToggleActive = async (id) => {
    try {
      await personnelAPI.toggleActive(id);
      toast.success('Durum güncellendi');
      fetchEmployees();
    } catch (error) {
      toast.error('Durum güncellenemedi');
    }
  };

  const filteredEmployees = employees.filter(emp =>
    emp.full_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Personel ara..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
              data-testid="search-employee"
            />
          </div>
        </div>

        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary-hover" data-testid="add-employee-btn">
              <Plus className="h-4 w-4 mr-2" />
              Yeni Personel
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Yeni Personel Ekle</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Ad Soyad *</Label>
                  <Input required value={formData.full_name} onChange={(e) => setFormData({ ...formData, full_name: e.target.value })} />
                </div>
                <div>
                  <Label>TC Kimlik No *</Label>
                  <Input required value={formData.identity_number} onChange={(e) => setFormData({ ...formData, identity_number: e.target.value })} />
                </div>
                <div>
                  <Label>Telefon *</Label>
                  <Input required value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} />
                </div>
                <div>
                  <Label>E-posta</Label>
                  <Input type="email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
                </div>
                <div>
                  <Label>Pozisyon *</Label>
                  <Input required value={formData.position} onChange={(e) => setFormData({ ...formData, position: e.target.value })} />
                </div>
                <div>
                  <Label>Departman</Label>
                  <Input value={formData.department} onChange={(e) => setFormData({ ...formData, department: e.target.value })} />
                </div>
                <div>
                  <Label>İşe Başlama Tarihi *</Label>
                  <Input type="date" required value={formData.hire_date} onChange={(e) => setFormData({ ...formData, hire_date: e.target.value })} />
                </div>
                <div>
                  <Label>Maaş (₺) *</Label>
                  <Input type="number" required value={formData.salary} onChange={(e) => setFormData({ ...formData, salary: e.target.value })} />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setShowDialog(false)}>İptal</Button>
                <Button type="submit" className="bg-primary hover:bg-primary-hover">Kaydet</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <div className="text-center py-12">Yükleniyor...</div>
      ) : filteredEmployees.length === 0 ? (
        <Card className="p-12 text-center">
          <p className="text-slate-600">Henüz personel eklenmemiş</p>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredEmployees.map((employee) => (
            <Card key={employee.id} className="p-6" data-testid={`employee-${employee.id}`}>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-bold text-slate-900">{employee.full_name}</h3>
                    {employee.is_active ? (
                      <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Aktif</span>
                    ) : (
                      <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">Pasif</span>
                    )}
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-slate-500">Pozisyon</p>
                      <p className="font-medium">{employee.position}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Departman</p>
                      <p className="font-medium">{employee.department || '-'}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Telefon</p>
                      <p className="font-medium">{employee.phone}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Maaş</p>
                      <p className="font-medium">₺{Number(employee.salary).toLocaleString('tr-TR')}</p>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleToggleActive(employee.id)}
                    data-testid={`toggle-${employee.id}`}
                  >
                    {employee.is_active ? <UserX className="h-4 w-4" /> : <UserCheck className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default EmployeeList;