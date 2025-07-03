import tkinter as tk
from datetime import date
from collections import defaultdict

# Initialize the lists to store data
goods_or_services = []
prices = []
dates = []
expense_types = []

def add_expense():
    expense_type = expense_type_var.get()
    good_or_service = good_or_service_entry.get()
    price = float(price_entry.get())
    today = date.today()

    goods_or_services.append(good_or_service)
    prices.append(price)
    dates.append(today)
    expense_types.append(expense_type)

    good_or_service_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

def show_expenses():
    expense_report = ""
    for expense_type, good_or_service, price, date in zip(expense_types, goods_or_services, prices, dates):
        expense_report += f"{expense_type} - {good_or_service} - {price} - {date}\n"
    report_label.config(text=expense_report)

def total_expenses_per_day():
    daily_expenses = defaultdict(float)
    for price, date in zip(prices, dates):
        daily_expenses[date] += price

    daily_expenses_report = ""
    for date, total in daily_expenses.items():
        daily_expenses_report += f"{date} - {total}\n"

    daily_expenses_label.config(text=daily_expenses_report)

app = tk.Tk()
app.title("Simple Expense Tracker")

expense_type_var = tk.StringVar()
expense_type_var.set("FOOD")
expense_type_dropdown = tk.OptionMenu(app, expense_type_var, "FOOD", "HOUSEHOLD", "TRANSPORTATION")
expense_type_dropdown.grid(row=0, column=0, padx=5, pady=5)

good_or_service_entry = tk.Entry(app)
good_or_service_entry.grid(row=1, column=0, padx=5, pady=5)

price_entry = tk.Entry(app)
price_entry.grid(row=2, column=0, padx=5, pady=5)

add_expense_button = tk.Button(app, text="Add Expense", command=add_expense)
add_expense_button.grid(row=3, column=0, padx=5, pady=5)

show_expenses_button = tk.Button(app, text="Show Expenses", command=show_expenses)
show_expenses_button.grid(row=4, column=0, padx=5, pady=5)

total_expenses_button = tk.Button(app, text="Total Expenses Per Day", command=total_expenses_per_day)
total_expenses_button.grid(row=5, column=0, padx=5, pady=5)

report_label = tk.Label(app, text="", justify=tk.LEFT)
report_label.grid(row=6, column=0, padx=5, pady=5)

daily_expenses_label = tk.Label(app, text="", justify=tk.LEFT)
daily_expenses_label.grid(row=7, column=0, padx=5, pady=5)

app.mainloop()