document.getElementById("add-to-cart-btn").addEventListener("click", async function () {
    const productId = this.dataset.productId;
    const quantity = document.getElementById("qty").value;

    const formData = new FormData();
    formData.append("product_id", productId);
    formData.append("quantity", quantity);

    const response = await fetch("/api/cart/add", {
        method: "POST",
        body: formData,
        credentials: "include"
    });

    if (response.status === 401) {
        window.location.href = "/login";
        return;
    }

    if (response.ok) {
        alert("Added to cart ✅");
    } else {
        const error = await response.json();
        alert(error.detail || "Something went wrong");
    }
});
