# 💸 Expense Tracker Applications

This repository contains two Python-based expense tracking applications:

### 📘 Simple Expense Tracker (`simpleexpensetracker.py`)

A basic Tkinter GUI app for quick expense tracking.

### 💼 Advanced Expense Tracker Pro (`advancexpensetracker.py`)

A feature-rich PyQt5 application with AI assistance, persistent database storage, currency conversion, visual charts, and export capabilities.

---

## 📑 Table of Contents

- [Simple Expense Tracker](#-simple-expense-tracker)
- [Advanced Expense Tracker Pro](#-advanced-expense-tracker-pro)
- [Installation](#️-installation)
- [Usage Instructions](#-usage-instructions)
- [Features Overview](#-features-overview)
- [Contributing](#-contributing)
- [Notes](#-notes)

---

## 📘 Simple Expense Tracker

### ✅ Features

- Add expenses with categories: `FOOD`, `HOUSEHOLD`, `TRANSPORTATION`
- View all expenses in a simple list
- Calculate total expenses per day
- Lightweight — no database (data stored in memory during session)

### 📦 Requirements

- Python 3.x
- Tkinter (comes with standard Python installation)

---

## 💼 Advanced Expense Tracker

A comprehensive expense management system with professional tools and automation.

### ✅ Features

- Persistent storage using SQLite database
- Multiple expense categories
- Multi-currency support with automatic conversion to USD
- Expense management: Add / Edit / Delete
- Visual charts: line and pie charts
- Export to CSV and PDF
- Date range filtering for summaries

### 📦 Requirements

- Python 3.7+
- PyQt5
- SQLite3
- Additional packages (see installation)

---

## ⚙️ Installation

### 📁 Step 1: Download the Project

#### OR download ZIP from GitHub and extract it.

### 🧾 Step 2: Using Simple Expense Tracker

```bash
# Run the basic tracker (no installation needed)
python simpleexpensetracker.py
```

### 🧠 Step 3: Using Advanced Expense Tracker

#### Create and activate a virtual environment:

```bash
# For Windows
python -m venv .venv
.venv\Scripts\activate

# For macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### Install the required packages:

```bash
pip install pillow matplotlib PyQt5 fpdf forex-python
```

#### Run the advanced application:

```bash
python advancexpensetracker.py
```

---

## 🚀 Usage Instructions

### 🧾 Simple Expense Tracker

- Select expense category (FOOD / HOUSEHOLD / TRANSPORTATION)
- Enter the description and amount
- Click **"Add Expense"**
- Use **"Show Expenses"** to view all entries
- Use **"Total Expenses Per Day"** for summary

### 🧠 Advanced Expense Tracker

This app is organized into four tabs:

#### 1. Add Expense

- Enter category, description, amount, currency, and date
- Supports multi-currency input (auto converts to USD)

#### 2. Manage Expenses

- View, edit, and delete records
- Filter by category or keyword
- Click any row and use **"Edit"** or **"Delete"**

#### 3. Summary

- Get total and average expenses by date range
- Category-wise breakdown
- Visual charts: line & pie

#### 4. Export

- Export filtered data to CSV
- Generate PDF reports
- Select category and date range for export

---

## 🧩 Features Overview

| Feature                | Simple Tracker | Advanced Tracker  |
| ---------------------- | -------------- | ----------------- |
| Add Expenses           | ✅             | ✅               |
| View & Filter Entries  | ✅             | ✅               |
| Categories             | ✅             | ✅               |
| Database Storage       | ❌             | ✅               |
| Multi-currency Support | ❌             | ✅               |
| Charts & Summary       | ❌             | ✅               |
| Export (CSV, PDF)      | ❌             | ✅               |

---

## 🤝 Contributing

Contributions, bug fixes, and feature suggestions are welcome!

- Open an issue if you encounter any problems
- Submit a pull request for improvements

---

## 📝 Notes

- The **Advanced Expense Tracker** creates an `expenses.db` file in the same directory
- Currency conversion requires an internet connection and uses **live exchange rates**





