

async function loadOrders() {
const res = await fetch("/api/orders", {});

    const orders = await res.json();
    const container = document.getElementById("orders");

    if (orders.length === 0) {
        container.innerHTML = "<p>No orders yet.</p>";
        return;
    }

    orders.forEach(o => {
        container.innerHTML += `
            <div style="border:1px solid #ccc; padding:10px; margin-bottom:10px">
                <p><b>Order ID:</b> ${o.id}</p>
                <p><b>Status:</b><span class="status ${o.status.toLowerCase()}">${o.status}</span></p>
                <p><b>Total:</b> ₹${o.amount}</p>
                <p><b>Date:</b> ${new Date(o.created_at).toLocaleString()}</p>
                <a href="/orders/${o.id}">View Details</a>
            </div>
        `;
    });
}

loadOrders();
                
                


