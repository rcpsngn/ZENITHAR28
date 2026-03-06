document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("auth-form");
    const toggleBtn = document.getElementById("toggle-auth");
    const emailField = document.getElementById("email-field");
    const companyField = document.getElementById("company-field");
    const passwordConfirmField = document.getElementById("password-confirm-field");

    let isLogin = true;

    toggleBtn.addEventListener("click", function () {
        isLogin = !isLogin;

        if (isLogin) {
            emailField.style.display = "none";
            companyField.style.display = "none";
            passwordConfirmField.style.display = "none";
            toggleBtn.innerText = "Hesabınız yok mu? Kayıt olun";
            document.getElementById("auth-title").innerText = "Giriş Yap";
        } else {
            emailField.style.display = "block";
            companyField.style.display = "block";
            passwordConfirmField.style.display = "block";
            toggleBtn.innerText = "Zaten hesabınız var mı? Giriş yapın";
            document.getElementById("auth-title").innerText = "Hesap Oluştur";
        }
    });


    form.addEventListener("submit", async function (e) {

        e.preventDefault();

        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const company = document.getElementById("company").value;
        const password = document.getElementById("password").value;
        const passwordConfirm = document.getElementById("password_confirm").value;

        if (!isLogin && password !== passwordConfirm) {
            alert("Şifreler eşleşmiyor!");
            return;
        }

        const url = isLogin
            ? "/api/auth/login/"
            : "/api/auth/register/";

        const data = {
            username: username,
            password: password
        };

        if (!isLogin) {
            data.email = email;
            data.company_name = company;
            data.password_confirm = passwordConfirm;
        }

        try {

            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                alert(result.detail || "Bir hata oluştu");
                return;
            }

            alert(isLogin ? "Giriş başarılı!" : "Hesap oluşturuldu!");

            localStorage.setItem("token", result.tokens.access);

            window.location.href = "/dashboard/";

        } catch (error) {

            alert("Sunucu hatası");

        }

    });

});