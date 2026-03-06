import { toast } from "../core/use-toast.js";

const EmployeeList = () => {

  const container = document.getElementById("employee-list");
  const searchInput = document.getElementById("employee-search");

  let employees = [];

  const getCookie = (name) => {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

      const cookies = document.cookie.split(";");

      for (let i = 0; i < cookies.length; i++) {

        const cookie = cookies[i].trim();

        if (cookie.substring(0, name.length + 1) === name + "=") {

          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));

          break;

        }

      }

    }

    return cookieValue;

  };

  const fetchEmployees = async () => {

    container.innerHTML = `<div class="text-center py-12">Yükleniyor...</div>`;

    try {

      const res = await fetch("/api/employees/");
      const data = await res.json();

      employees = data || [];

      renderEmployees();

    } catch (error) {

      console.error(error);
      toast.error("Personeller yüklenemedi");

    }

  };

  const handleToggleActive = async (id) => {

    try {

      const res = await fetch(`/api/employees/${id}/toggle-active/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken")
        }
      });

      if (!res.ok) throw new Error();

      toast.success("Durum güncellendi");

      fetchEmployees();

    } catch {

      toast.error("Durum güncellenemedi");

    }

  };

  const renderEmployees = () => {

    const searchTerm = searchInput.value.toLowerCase();

    const filtered = employees.filter(emp =>
      emp.full_name?.toLowerCase().includes(searchTerm)
    );

    if (filtered.length === 0) {

      container.innerHTML = `
        <div class="p-12 text-center border rounded-lg bg-white">
          <p class="text-slate-600">Henüz personel eklenmemiş</p>
        </div>
      `;

      return;

    }

    let html = `<div class="grid gap-4">`;

    filtered.forEach(employee => {

      html += `

      <div class="p-6 border rounded-lg bg-white">

        <div class="flex justify-between items-start">

          <div class="flex-1">

            <div class="flex items-center gap-3 mb-2">

              <h3 class="text-lg font-bold text-slate-900">
                ${employee.full_name}
              </h3>

              ${
                employee.is_active
                  ? `<span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Aktif</span>`
                  : `<span class="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">Pasif</span>`
              }

            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">

              <div>
                <p class="text-slate-500">Pozisyon</p>
                <p class="font-medium">${employee.position}</p>
              </div>

              <div>
                <p class="text-slate-500">Departman</p>
                <p class="font-medium">${employee.department || "-"}</p>
              </div>

              <div>
                <p class="text-slate-500">Telefon</p>
                <p class="font-medium">${employee.phone}</p>
              </div>

              <div>
                <p class="text-slate-500">Maaş</p>
                <p class="font-medium">
                  ₺${Number(employee.salary).toLocaleString("tr-TR")}
                </p>
              </div>

            </div>

          </div>

          <div class="flex gap-2">

            <button
              class="toggle-btn px-3 py-1 border rounded text-sm hover:bg-slate-50"
              data-id="${employee.id}"
            >
              ${employee.is_active ? "Pasif Yap" : "Aktif Yap"}
            </button>

          </div>

        </div>

      </div>

      `;

    });

    html += `</div>`;

    container.innerHTML = html;

    document.querySelectorAll(".toggle-btn").forEach(btn => {

      btn.addEventListener("click", () => {

        const id = btn.dataset.id;

        handleToggleActive(id);

      });

    });

  };

  searchInput.addEventListener("input", renderEmployees);

  fetchEmployees();

};

export default EmployeeList;