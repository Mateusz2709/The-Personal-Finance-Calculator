# Personal Finance Calculator 🧮💷

A Python-based terminal application that helps users manage their personal finances by tracking income, recording expenses, and generating budget summaries and reports. It supports both registered user accounts (with secure password hashing) and guest sessions.

## 🚀 Features

- 🔐 User registration and login with SHA-256 password hashing  
- 💼 Income entry and profile-based storage  
- 🧾 Expense tracking by category, type, and date  
- 📊 Budget summary with spending feedback  
- 📈 Report generation by category, date range, or type (Essential/Non-Essential)  
- 👤 Guest mode (no account required)  
- 🗑️ Account deletion and data reset  
- 📄 CSV-based data storage  
- 📋 Tabulated output using `tabulate`  
- 🪵 Activity logging using `logging` module

## 📁 File Structure

- `main.py` – Main application logic  
- `user_list.csv` – Stores registered users and their income  
- `expenses.csv` – Stores user and guest expenses  
- `app.log` – Logs user activity and errors

## 🛠 Requirements

- Python 3.x  
- `tabulate` module

To install `tabulate`:

```bash
pip install tabulate
```

## ▶️ How to Run

Run the application from your terminal:

```bash
python main.py
```

Then follow the on-screen prompts to create a profile, login, or use the app as a guest.

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Mateusz Malerek**  
Software Engineering Student – University of Bolton

