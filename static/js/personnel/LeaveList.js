import { personnelAPI } from "../core/api.js";
import { toast } from "../core/use-toast.js";

const LeaveList = () => {

  const container = document.getElementById("leave-list");

  const leaveTypes = {
    annual: "Yıllık",
    sick: "Hastalık",
    unpaid: "Ücretsiz",
    maternity: "Doğum",
    other: "Diğer",
  };

  const loadLeaves = async () => {

    container.innerHTML = `
      <div class="text-center py-12 text-slate-500">
        İzinler yükleniyor...
      </div>
    `;

    try {

      const res = await personnelAPI.getLeaves();
      const leaves = res.data || [];

      if (leaves.length === 0) {
        container.innerHTML = `
          <div class="p-12 text-center border rounded-lg bg-white">
            <p class="text-slate-600">Henüz izin talebi yok</p>
          </div>
        `;
        return;
      }

      let html = `<div class="grid gap-4">`;

      leaves.forEach((leave) => {

        html += `
        <div class="p-6 border rounded-lg bg-white">
          <div class="flex justify-between items-start">

            <div class="flex-1">

              <div class="flex items-center gap-3 mb-2">
                <h3 class="font-bold text-lg">${leave.employee_name}</h3>

                <span class="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                  ${leaveTypes[leave.type] || leave.type}
                </span>

                ${
                  leave.status === "pending"
                    ? `<span class="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">Bekliyor</span>`
                    : ""
                }

                ${
                  leave.status === "approved"
                    ? `<span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Onaylandı</span>`
                    : ""
                }

                ${
                  leave.status === "rejected"
                    ? `<span class="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">Reddedildi</span>`
                    : ""
                }
              </div>

              <div class="grid grid-cols-3 gap-4 text-sm mb-2">

                <div>
                  <p class="text-slate-500">Başlangıç</p>
                  <p class="font-medium">
                    ${new Date(leave.start_date).toLocaleDateString("tr-TR")}
                  </p>
                </div>

                <div>
                  <p class="text-slate-500">Bitiş</p>
                  <p class="font-medium">
                    ${new Date(leave.end_date).toLocaleDateString("tr-TR")}
                  </p>
                </div>

                <div>
                  <p class="text-slate-500">Gün</p>
                  <p class="font-medium">${leave.days} gün</p>
                </div>

              </div>

              ${
                leave.reason
                  ? `<p class="text-sm text-slate-600">${leave.reason}</p>`
                  : ""
              }

            </div>

            ${
              leave.status === "pending"
                ? `
                <div class="flex gap-2">

                  <button
                    class="approve-btn px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm"
                    data-id="${leave.id}"
                  >
                    Onayla
                  </button>

                  <button
                    class="reject-btn px-3 py-1 border text-red-600 hover:bg-red-50 rounded text-sm"
                    data-id="${leave.id}"
                  >
                    Reddet
                  </button>

                </div>
                `
                : ""
            }

          </div>
        </div>
        `;
      });

      html += `</div>`;

      container.innerHTML = html;

      document.querySelectorAll(".approve-btn").forEach(btn => {
        btn.addEventListener("click", async () => {

          const id = btn.dataset.id;

          try {
            await personnelAPI.approveLeave(id);
            toast.success("İzin onaylandı");
            loadLeaves();
          } catch {
            toast.error("Onaylama başarısız");
          }

        });
      });

      document.querySelectorAll(".reject-btn").forEach(btn => {
        btn.addEventListener("click", async () => {

          const id = btn.dataset.id;

          try {
            await personnelAPI.rejectLeave(id, "Reddedildi");
            toast.success("İzin reddedildi");
            loadLeaves();
          } catch {
            toast.error("Reddetme başarısız");
          }

        });
      });

    } catch {
      toast.error("İzinler yüklenemedi");
    }
  };

  loadLeaves();
};

export default LeaveList;