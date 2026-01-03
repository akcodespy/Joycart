const PRODUCT_ID = getProductIdFromUrl();

document.addEventListener("DOMContentLoaded", () => {
    loadRating();
    loadReviews();
});

function getProductIdFromUrl() {
    const parts = window.location.pathname.split("/");
    return parts[parts.length - 1];
}

async function loadRating() {
    const res = await fetch(`/api/reviews/calculate?product_id=${PRODUCT_ID}`);
    const data = await res.json();

    document.getElementById("rating-summary").innerText =
        `⭐ ${data.average_rating} / 5 (${data.total_reviews} reviews)`;
}

async function loadReviews() {
    const res = await fetch(`/api/reviews/load?product_id=${PRODUCT_ID}`);
    const reviews = await res.json();

    const container = document.getElementById("reviews-list");
    container.innerHTML = "";

    if (reviews.length === 0) {
        container.innerHTML = "<p>No reviews yet.</p>";
        return;
    }

        reviews.forEach(r => {
        const div = document.createElement("div");
        div.className = "review";

        div.innerHTML = `
            <div class="review-user"><b>${r.username}</b></div><br>
            <div class="review-rating">Rating: ${r.rating} / 5</div><br>
            ${r.comment ? `<div class="review-comment">Review :${r.comment}</div>` : ""}
        `;

        container.appendChild(div);
    });
}

async function submitReview() {
    const rating = document.getElementById("rating").value;
    const comment = document.getElementById("comment").value;
    const message = document.getElementById("review-message");

    message.innerText = "";

    if (!rating) {
        message.innerText = "Please select a rating";
        return;
    }

    const formData = new FormData();
    formData.append("product_id", PRODUCT_ID);
    formData.append("rating", rating);
    formData.append("comment", comment);

    const res = await fetch("/api/reviews/add", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    if (!res.ok) {
        message.innerText = data.detail || "Failed to add review";
        return;
    }

    
    document.getElementById("rating").value = "";
    document.getElementById("comment").value = "";
    message.style.color = "green";
    message.innerText = "Review added successfully";

    
    loadRating();
    loadReviews();
}
