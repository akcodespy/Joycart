# 🛒 JoyCart – Full-Stack E-commerce Backend (FastAPI)

JoyCart is a **backend-first e-commerce application** built with **FastAPI**, focusing on real-world order flows, payments, refunds, seller operations, and webhook-driven state management.

This project was built to **learn and demonstrate production-style backend design**, especially around **payments, refunds, and transactional safety**.

---

## 🧱 Architecture Overview

JoyCart follows a **layered backend architecture**:

- **API Layer** – FastAPI routers (users, sellers, cart, checkout, orders)
- **Business Logic Layer** – order creation, stock handling, refunds
- **Persistence Layer** – SQLAlchemy ORM with PostgreSQL / SQLite
- **External Services**
  - Razorpay (payments & refunds)
  - Cloudinary (image storage)

The system is designed to be **state-driven**, meaning:
> UI never guesses payment/refund status — everything is read from the database.

---

## 🔐 Authentication & Roles

### 👤 Users
- JWT-based authentication
- Can:
  - Browse products
  - Add to cart
  - Checkout
  - Cancel individual order items
  - View order & refund status

### 🧑‍💼 Sellers
- Separate seller authentication
- Can:
  - Create / edit / delete products
  - Upload images (thumbnail + gallery)
  - Manage stock
  - Update order item status (confirm, ship, deliver, cancel)

---

## 🛍️ Product Management

- Products belong to a seller
- Fields include:
  - Price & discount
  - Stock quantity
  - Availability status
  - Dimensions stored as JSON
- Images handled via **Cloudinary**
- Product edits support **partial updates**
- Seller ownership is strictly enforced

---

## 🛒 Cart & Checkout Flow

1. User adds items to cart
2. Cart validates stock
3. Checkout session is created with expiry
4. Razorpay order is generated
5. Payment is completed asynchronously
6. Order is created only after payment confirmation

Duplicate order creation is prevented using:
- checkout ownership checks
- idempotent order creation logic

---

## 💳 Payments (Razorpay)

- Razorpay Orders API used for payment initiation
- Payments are confirmed **only via webhook**
- Signature verification using HMAC SHA256
- Payment status stored in DB (`SUCCESS`, `FAILED`, etc.)

The backend **never trusts frontend payment success**.

---

## 🔄 Refund System (Key Feature)

Refunds are implemented in a **production-correct, webhook-based way**.

### Refund Design Principles
- Refunds are **asynchronous**
- Database state is committed **before** calling Razorpay
- Refund success is **never assumed**
- Final status is updated **only via webhook**

### Refund Flow

1. User/Seller cancels an order item
2. Item status → `CANCELLED`
3. Stock is restored
4. Refund record created (`INITIATED`)
5. Razorpay refund API is called
6. Razorpay sends webhook:
   - `refund.processed` → status becomes `REFUNDED`
   - `refund.failed` → status becomes `FAILED`

Refunds are **item-level**, allowing partial refunds per order.

---

## 📡 Webhooks

### Supported Razorpay Events
- `payment.captured`
- `refund.processed`
- `refund.failed`

### Security
- All webhooks verified using Razorpay webhook secret
- Invalid signatures are ignored
- Webhooks are idempotent and safe to retry

---

## 🧠 Transaction & Error Handling

- External API calls happen **after DB commit**
- Database consistency is preserved even if Razorpay fails
- Refund retries are safe
- Duplicate cancellations are prevented
- Seller and user flows share the same refund logic

---

## ☁️ Deployment & Environment

### Local Development
- SQLite database
- Razorpay TEST mode
- **ngrok required** for webhook testing

```bash
ngrok http 8000
