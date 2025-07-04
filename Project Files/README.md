# 🥒 Home Made Pickles – A Flask Web App

Home Made Pickles is a user-friendly Flask web application for browsing, selecting, and ordering delicious home-made vegetarian, non-vegetarian pickles and snacks. It features a login/signup system, a product catalog, a shopping cart, and a checkout process — all wrapped in a clean, responsive UI.

---

## 📌 Features

- ✅ User Signup & Login
- ✅ Product filtering (Veg, Non-Veg, Snacks)
- ✅ Add to Cart, View Cart, Remove Items
- ✅ Update Item Quantity
- ✅ Checkout with cart-clearing logic
- ✅ Flash messages & form validations
- ✅ Responsive design with custom styling
- ✅ Clean project structure for easy deployment

---

## 🛠 Tech Stack

| Layer      | Technology      |
|------------|-----------------|
| Backend    | Python, Flask   |
| Frontend   | HTML, CSS, Jinja2 |
| Data       | JSON files (no DB) |
| Deployment | Runs locally (`localhost:5000`) |

---

## 🏗️ Project Structure

```
home-made-pickles/
├── app.py
├── users.json
├── requirements.txt
├── .gitignore
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── products.html
│   ├── cart.html
│   ├── checkout.html
│   ├── success.html
│   └── base.html
├── static/
│   ├── style.css
│   └── images/
```

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/home-made-pickles.git
cd home-made-pickles
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # On Windows
source venv/bin/activate     # On macOS/Linux
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the App

```bash
python app.py
```

Visit: [http://localhost:5000](http://localhost:5000)

---

## 📦 Sample Users

```json
{
  "users": [
    {
      "name": "testuser",
      "email": "test@example.com",
      "password": "1234"
    }
  ]
}
```

---

## 📌 Future Enhancements

- Admin panel to manage products
- Switch to SQLite or MySQL database
- Razorpay/Stripe payment integration
- Deployed version on PythonAnywhere or Render

---

## 👨‍💻 Author

 [Narasimha Naidu](https://github.com/NarasimhaNaidu04)
