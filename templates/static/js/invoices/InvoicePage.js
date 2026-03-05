import React, { useState, useEffect } from 'react';
import { Plus, Search, FileText } from 'lucide-react';
import Button from '../../components/ui/button'
import Input from '../../components/ui/input';
import Card from '../../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import Label from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { invoiceAPI } from '../../services/api';
import { toast } from 'sonner';

const InvoicePage = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [formData, setFormData] = useState({
    type: 'e-fatura',
    invoice_number: '',
    customer_name: '',
    customer_tax_id: '',
    amount: '',
    vat_rate: '20',
    issue_date: '',
    status: 'draft',
    items: []
  });

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      const response = await invoiceAPI.getInvoices();
      setInvoices(response.data || []);
    } catch (error) {
      console.error('Fetch error:', error);
      toast.error('Faturalar yüklenemedi');
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const vat_amount = (parseFloat(formData.amount) * parseFloat(formData.vat_rate)) / 100;
      const total_amount = parseFloat(formData.amount) + vat_amount;
      
      await invoiceAPI.createInvoice({
        ...formData,
        amount: parseFloat(formData.amount),
        vat_amount,
        total_amount,
        vat_rate: parseFloat(formData.vat_rate)
      });
      
      toast.success('Fatura oluşturuldu');
      setShowDialog(false);
      fetchInvoices();
      setFormData({ type: 'e-fatura', invoice_number: '', customer_name: '', customer_tax_id: '', amount: '', vat_rate: '20', issue_date: '', status: 'draft', items: [] });
    } catch (error) {
      toast.error('Fatura oluşturulamadı');
    }
  };

  const filteredInvoices = (invoices || []).filter(inv => 
    inv.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inv.invoice_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadge = (status) => {
    const badges = {
      draft: { label: 'Taslak', class: 'bg-gray-100 text-gray-700' },
      sent: { label: 'Gönderildi', class: 'bg-blue-100 text-blue-700' },
      paid: { label: 'Ödendi', class: 'bg-green-100 text-green-700' },
      cancelled: { label: 'İptal', class: 'bg-red-100 text-red-700' }
    };
    const badge = badges[status] || badges.draft;
    return <span className={`px-2 py-1 rounded-full text-xs ${badge.class}`}>{badge.label}</span>;
  };

  return (
    <div data-testid="invoice-page">
      <div className="mb-6">
        <h1 className="text-3xl font-manrope font-bold text-slate-900 mb-2">
          E-Fatura / E-İrsaliye
        </h1>
        <p className="text-slate-600">
          Faturalarınızı oluşturun, yönetin ve takip edin
        </p>
      </div>

      <div className="flex justify-between items-center mb-6">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Fatura veya müşteri ara..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
              data-testid="search-invoice"
            />
          </div>
        </div>
        
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary-hover" data-testid="add-invoice-btn">
              <Plus className="h-4 w-4 mr-2" />
              Yeni Fatura
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Yeni Fatura Oluştur</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Fatura Tipi *</Label>
                  <Select value={formData.type} onValueChange={(v) => setFormData({...formData, type: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="e-fatura">E-Fatura</SelectItem>
                      <SelectItem value="e-irsaliye">E-İrsaliye</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Fatura No *</Label>
                  <Input required value={formData.invoice_number} onChange={(e) => setFormData({...formData, invoice_number: e.target.value})} />
                </div>
                <div>
                  <Label>Müşteri Adı *</Label>
                  <Input required value={formData.customer_name} onChange={(e) => setFormData({...formData, customer_name: e.target.value})} />
                </div>
                <div>
                  <Label>Vergi No</Label>
                  <Input value={formData.customer_tax_id} onChange={(e) => setFormData({...formData, customer_tax_id: e.target.value})} />
                </div>
                <div>
                  <Label>Tutar (₺) *</Label>
                  <Input type="number" step="0.01" required value={formData.amount} onChange={(e) => setFormData({...formData, amount: e.target.value})} />
                </div>
                <div>
                  <Label>KDV Oranı (%) *</Label>
                  <Select value={formData.vat_rate} onValueChange={(v) => setFormData({...formData, vat_rate: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">%1</SelectItem>
                      <SelectItem value="10">%10</SelectItem>
                      <SelectItem value="20">%20</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Fatura Tarihi *</Label>
                  <Input type="date" required value={formData.issue_date} onChange={(e) => setFormData({...formData, issue_date: e.target.value})} />
                </div>
                <div>
                  <Label>Durum *</Label>
                  <Select value={formData.status} onValueChange={(v) => setFormData({...formData, status: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Taslak</SelectItem>
                      <SelectItem value="sent">Gönderildi</SelectItem>
                      <SelectItem value="paid">Ödendi</SelectItem>
                    </SelectContent>
                  </Select>
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
      ) : filteredInvoices.length === 0 ? (
        <Card className="p-12 text-center">
          <FileText className="h-12 w-12 mx-auto mb-4 text-slate-400" />
          <p className="text-slate-600">Henüz fatura eklenmemiş</p>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredInvoices.map((invoice) => (
            <Card key={invoice.id} className="p-6" data-testid={`invoice-${invoice.id}`}>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-bold text-slate-900">{invoice.invoice_number}</h3>
                    {getStatusBadge(invoice.status)}
                    <span className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs rounded-full">
                      {invoice.type === 'e-fatura' ? 'E-Fatura' : 'E-İrsaliye'}
                    </span>
                  </div>
                  <p className="text-slate-600 mb-3">{invoice.customer_name}</p>
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-slate-500">Tarih</p>
                      <p className="font-medium">{new Date(invoice.issue_date).toLocaleDateString('tr-TR')}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Tutar</p>
                      <p className="font-medium">₺{Number(invoice.amount).toLocaleString('tr-TR', {minimumFractionDigits: 2})}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">KDV</p>
                      <p className="font-medium">₺{Number(invoice.vat_amount).toLocaleString('tr-TR', {minimumFractionDigits: 2})}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Toplam</p>
                      <p className="font-bold text-lg">₺{Number(invoice.total_amount).toLocaleString('tr-TR', {minimumFractionDigits: 2})}</p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default InvoicePage;
