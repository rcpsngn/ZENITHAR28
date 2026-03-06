import { personnelAPI } from "../core/api.js";
import { toast } from "../core/use-toast.js";

const SalaryList = () => {

  const container = document.getElementById("salary-list");
  if (!container) return;

  const fetchSalaries = async () => {

    container.innerHTML = `<div class="text-center py-12">Yükleniyor...</div>`;

    try {

      const response = await personnelAPI.getSalaries();
      const salaries = response?.data || [];

      if (salaries.length === 0) {
        container.innerHTML = `
          <div class="p-12 text-center">
            <p class="text-slate-600">Henüz maaş kaydı yok</p>
          </div>
        `;
        return;
      }

      let html = `<div class="grid gap-4">`;

      salaries.forEach((salary) => {

        html += `
        <div class="p-6 border rounded-lg bg-white">
          <div class="flex justify-between items-start">

            <div>
              <h3 class="font-bold text-lg mb-2">${salary.employee_name}</h3>
              <p class="text-slate-600 mb-4">${salary.month_name} ${salary.year}</p>

              <div class="grid grid-cols-4 gap-4 text-sm">

                <div>
                  <p class="text-slate-500">Temel</p>
                  <p class="font-medium">₺${Number(salary.base_salary || 0).toLocaleString('tr-TR')}</p>
                </div>

                <div>
                  <p class="text-slate-500">Prim</p>
                  <p class="font-medium text-green-600">+₺${Number(salary.bonus || 0).toLocaleString('tr-TR')}</p>
                </div>

                <div>
                  <p class="text-slate-500">Kesinti</p>
                  <p class="font-medium text-red-600">-₺${Number(salary.deductions || 0).toLocaleString('tr-TR')}</p>
                </div>

                <div>
                  <p class="text-slate-500">Net</p>
                  <p class="font-bold text-lg">₺${Number(salary.net_salary || 0).toLocaleString('tr-TR')}</p>
                </div>

              </div>
            </div>

            <div class="text-right">
              ${
                salary.status === "paid"
                  ? `<span class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">Ödendi</span>`
                  : `<button class="pay-btn px-3 py-1 bg-blue-600 text-white rounded text-sm" data-id="${salary.id}">
                        Öde
                     </button>`
              }
            </div>

          </div>
        </div>
        `;
      });

      html += `</div>`;

      container.innerHTML = html;

      document.querySelectorAll(".pay-btn").forEach(btn => {

        btn.addEventListener("click", async () => {

          const id = btn.dataset.id;

          try {
            await personnelAPI.markPaid(id);
            toast.success("Ödendi olarak işaretlendi");
            fetchSalaries();
          } catch {
            toast.error("İşlem başarısız");
          }

        });

      });

    } catch {
      toast.error("Maaşlar yüklenemedi");
    }
  };

  fetchSalaries();
};

export default SalaryList;