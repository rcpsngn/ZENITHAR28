import React, { useState, useEffect } from 'react';
import { Plus, Search, FileText } from 'lucide-react';
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
    status: 'draft'
  });

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {

      const response = await fetch("/api/invoices/");
      const data = await response.json();
      setInvoices(data);

    } catch (error) {

      console.error("Fetch error:", error);
      toast.error("Faturalar yüklenemedi");

    } finally {

      setLoading(false);

    }
  };

  const getCookie = (name) => {

    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {

      const cookies = document.cookie.split(';');

      for (let i = 0; i < cookies.length; i++) {

        const cookie = cookies[i].trim();

        if (cookie.substring(0, name.length + 1) === (name + '=')) {

          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));

          break;

        }

      }

    }

    return cookieValue;

  };

  const handleSubmit = async (e) => {

    e.preventDefault();

    try {

      const vat_amount = (parseFloat(formData.amount) * parseFloat(formData.vat_rate)) / 100;
      const total_amount = parseFloat(formData.amount) + vat_amount;

      const response = await fetch("/api/invoices/create/", {

        method: "POST",

        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },

        body: JSON.stringify({
          ...formData,
          amount: parseFloat(formData.amount),
          vat_amount,
          total_amount,
          vat_rate: parseFloat(formData.vat_rate)
        })

      });

      if (!response.ok) throw new Error();

      toast.success("Fatura oluşturuldu");

      setShowDialog(false);

      fetchInvoices();

      setFormData({
        type: 'e-fatura',
        invoice_number: '',
        customer_name: '',
        customer_tax_id: '',
        amount: '',
        vat_rate: '20',
        issue_date: '',
        status: 'draft'
      });

    } catch (error) {

      toast.error("Fatura oluşturulamadı");

    }

  };

  const filteredInvoices = invoices.filter(inv =>
    inv.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inv.invoice_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (

    <div className="p-6">

      <div className="mb-6">

        <h1 className="text-3xl font-bold text-slate-900 mb-2">
          E-Fatura / E-İrsaliye
        </h1>

        <p className="text-slate-600">
          Faturalarınızı oluşturun ve yönetin
        </p>

      </div>

      <div className="flex justify-between items-center mb-6">

        <div className="flex-1 max-w-md">

          <div className="relative">

            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />

            <input
              className="w-full border rounded-lg pl-10 pr-3 py-2"
              placeholder="Fatura veya müşteri ara..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />

          </div>

        </div>

        <button
          onClick={() => setShowDialog(true)}
          className="flex items-center bg-blue-600 text-white px-4 py-2 rounded-lg"
        >
          <Plus className="h-4 w-4 mr-2" />
          Yeni Fatura
        </button>

      </div>

      {loading ? (

        <div className="text-center py-12">Yükleniyor...</div>

      ) : filteredInvoices.length === 0 ? (

        <div className="border rounded-lg p-12 text-center">

          <FileText className="h-12 w-12 mx-auto mb-4 text-slate-400" />

          <p className="text-slate-600">Henüz fatura eklenmemiş</p>

        </div>

      ) : (

        <div className="grid gap-4">

          {filteredInvoices.map((invoice) => (

            <div key={invoice.id} className="border rounded-lg p-6">

              <h3 className="text-lg font-bold">
                {invoice.invoice_number}
              </h3>

              <p>{invoice.customer_name}</p>

              <p>
                ₺{Number(invoice.total_amount).toLocaleString('tr-TR', {
                  minimumFractionDigits: 2
                })}
              </p>

            </div>

          ))}

        </div>

      )}

    </div>

  );
};

export default InvoicePage;