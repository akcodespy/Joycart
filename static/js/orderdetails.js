async function loadOrder() {
    const orderId = window.location.pathname.split("/").pop();

    const res = await fetch(`/api/orders/${orderId}`, {});

    const order = await res.json();
    const container = document.getElementById("order");

    container.innerHTML = `
        <p><b>Order ID:</b> ${order.id}</p>
        <p><b>Status:</b> ${order.status}</p>

        <hr>
    `;

    order.items.forEach(item => {
        container.innerHTML += `
            <div style="margin-bottom:10px">
                <p>${item.title}</p>
                <p>Price: ₹${item.price}</p>
                <p>Qty: ${item.quantity}</p>
                <p>Subtotal: ₹${item.subtotal}</p>
            </div>
        `;
    });
if (order.status === "PLACED"|| order.status === "PAID") {
        container.innerHTML += `
            <hr>
            <p><b>Total : </b> ₹${order.amount}</p>
            <button onclick="cancelOrder(${order.id})">
                Cancel Order
            </button><br></br>
        <a href="/">Home</a>
    `;
}
else if (order.status === "REFUNDED"){
        container.innerHTML += `
        <hr>
        <p><b>Total : </b> ₹${order.amount}</p>
        <p><b>Refund ID:</b> ${order.payment}</p>
        <a href="/">Home</a>
    `;
}
else if (order.status === "CANCELLED") {
    container.innerHTML += `
        <hr>
        <p><b>Total : </b> ₹${order.amount}</p>
        <a href="/">Home</a>
    `;
}
}
async function cancelOrder(orderId) {
    
    const confirmCancel = confirm("Are you sure you want to cancel this order?");
    if (!confirmCancel) return;

    const res = await fetch(`/api/orders/cancel/${orderId}`, {
        method: "POST",});

    if (!res.ok) {
        const errorData = await res.json();
        alert(errorData.detail || "Unable to cancel order");
        return;
    }

    alert("Order cancelled successfully");

    window.location.reload();

}


loadOrder();