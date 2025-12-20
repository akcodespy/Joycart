const orderId = window.location.pathname.split("/").pop();

async function getOrder() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        window.location.href = "/login";
        return;
    }

    const res = await fetch(`/api/orders/${orderId}`, {
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    if (!res.ok) {
        alert("Order not found");
        return;
    }

    const order = await res.json();
    const container = document.getElementById("items");

    container.innerHTML = `
        <p><b>Order ID:</b> ${order.id}</p>
        <p><b>Status:</b> ${order.status}</p>
        <p><b>Total:</b> ₹${order.amount}</p>
        <hr>
    `;

    if (order.status === "PENDING") {
        container.innerHTML += `
            <button id="pay-btn">Pay Now</button>
        `;

        document
            .getElementById("pay-btn")
            .addEventListener("click", payNow);
    }
}

async function payNow() {
    const res = await fetch(`/api/payments?order_id=${orderId}`, {
        method: "POST"
    });

    if (!res.ok) {
        const errorData = await res.json();
        alert(errorData.detail || "Payment failed");
        return;
    }

    window.location.href = `/payment-success/${orderId}`;
}

getOrder();
