const fastToken = localStorage.getItem("access_token");
  if (fastToken && window.location.pathname !== '/dashboard') {
    window.location.href = '/dashboard';
  }
        const msg = document.getElementById("msg");
        const form = document.getElementById("login-form");

        function setMsg(type, text) {
            msg.className = type;
            msg.textContent = text;
            msg.style.display = "block";
        }
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const payload = {
                username: document.getElementById("username").value,
                password: document.getElementById("password").value,
            };

            setMsg("status", "Signing in...");

            try {
                const res = await fetch("/api/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });

                const data = await res.json();

                if (!res.ok) {
                    setMsg("error", data?.detail || "Invalid credentials");
                    return;
                }

                const token = data.access_token;

                localStorage.setItem("access_token", token);
                localStorage.setItem("username", data.username);


                document.cookie = "access_token=" + encodeURIComponent(token) + "; path=/";

                setMsg("success", "Login successful! Redirecting...");
                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 500);

            } catch (err) {
                setMsg("error", "Network error");
            }
        });