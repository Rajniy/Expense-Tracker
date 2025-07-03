import sys
import csv
import sqlite3
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDateEdit, QMessageBox, QTextEdit, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog, QFormLayout,
    QDialogButtonBox, QFileDialog, QVBoxLayout, QGroupBox
)
from PyQt5.QtCore import Qt, QDate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from fpdf import FPDF
from forex_python.converter import CurrencyRates

# Database setup
conn = sqlite3.connect('expenses.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_type TEXT,
    good_or_service TEXT,
    price REAL,
    currency TEXT DEFAULT 'USD',
    date TEXT
)
''')
conn.commit()

default_categories = ["FOOD", "HOUSEHOLD", "TRANSPORTATION", "ENTERTAINMENT", "HEALTH", "OTHER"]

class EditExpenseDialog(QDialog):
    def __init__(self, expense_id, expense_type, good_or_service, price, currency, date_str, categories, parent=None):
        super().__init__(parent)
        self.expense_id = expense_id
        self.categories = categories
        self.setWindowTitle("Edit Expense")

        self.layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Expense type
        self.expense_type_combo = QComboBox()
        self.expense_type_combo.addItems(self.categories)
        self.expense_type_combo.setCurrentText(expense_type)
        form_layout.addRow(QLabel("Expense Type:"), self.expense_type_combo)

        # Good or Service
        self.good_service_input = QLineEdit(good_or_service)
        form_layout.addRow(QLabel("Good or Service:"), self.good_service_input)

        # Price and Currency
        price_layout = QHBoxLayout()
        self.price_input = QLineEdit(str(price))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "EUR", "GBP", "JPY", "INR"])
        self.currency_combo.setCurrentText(currency)
        price_layout.addWidget(self.price_input)
        price_layout.addWidget(self.currency_combo)
        form_layout.addRow(QLabel("Price:"), price_layout)

        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
        form_layout.addRow(QLabel("Date:"), self.date_input)

        self.layout.addLayout(form_layout)

        # Dialog buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.save_changes)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def save_changes(self):
        good_or_service = self.good_service_input.text().strip()
        price_text = self.price_input.text().strip()
        expense_type = self.expense_type_combo.currentText()
        currency = self.currency_combo.currentText()
        expense_date = self.date_input.date().toPyDate()

        if not good_or_service:
            QMessageBox.warning(self, "Input Error", "Please enter a good or service.")
            return
        try:
            price = float(price_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid price.")
            return

        c.execute('''UPDATE expenses SET 
                  expense_type = ?, 
                  good_or_service = ?, 
                  price = ?,
                  currency = ?,
                  date = ?
                  WHERE id = ?''',
                  (expense_type, good_or_service, price, currency, 
                   expense_date.strftime('%Y-%m-%d'), self.expense_id))
        conn.commit()
        self.accept()

class ExpenseTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Expense Tracker Pro")
        self.setGeometry(100, 100, 1200, 800)
        self.categories = default_categories.copy()
        self.currencies = ["USD", "EUR", "GBP", "JPY", "INR"]
        self.currency_rates = CurrencyRates()
        
        # Initialize tabs before UI setup
        self.tab_add_expense = QWidget()
        self.tab_manage_expenses = QWidget()
        self.tab_summary = QWidget()
        self.tab_export = QWidget()
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        
        # Add tabs before initializing them
        self.tabs.addTab(self.tab_add_expense, "Add Expense")
        self.tabs.addTab(self.tab_manage_expenses, "Manage Expenses")
        self.tabs.addTab(self.tab_summary, "Summary")
        self.tabs.addTab(self.tab_export, "Export")

        # Initialize all tabs
        self.init_tab_add_expense()
        self.init_tab_manage_expenses()
        self.init_tab_summary()
        self.init_tab_export()

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def init_tab_add_expense(self):
        layout = QVBoxLayout(self.tab_add_expense)

        # Expense type
        type_group = QGroupBox("Expense Details")
        type_layout = QVBoxLayout()

        category_layout = QHBoxLayout()
        self.expense_type_combo = QComboBox()
        self.expense_type_combo.addItems(self.categories)
        category_layout.addWidget(QLabel("Expense Type:"))
        category_layout.addWidget(self.expense_type_combo)
        type_layout.addLayout(category_layout)

        # Good or Service input
        self.good_service_input = QLineEdit()
        self.good_service_input.setPlaceholderText("Good/Service")
        type_layout.addWidget(self.good_service_input)

        # Price and Currency
        price_layout = QHBoxLayout()
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(self.currencies)
        price_layout.addWidget(QLabel("Amount:"))
        price_layout.addWidget(self.price_input)
        price_layout.addWidget(self.currency_combo)
        type_layout.addLayout(price_layout)

        # Date input
        date_layout = QHBoxLayout()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("Date:"))
        date_layout.addWidget(self.date_input)
        type_layout.addLayout(date_layout)

        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Add Expense button
        self.add_expense_btn = QPushButton("Add Expense")
        self.add_expense_btn.clicked.connect(self.add_expense)
        self.add_expense_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        layout.addWidget(self.add_expense_btn)

    def add_expense(self):
        expense_type = self.expense_type_combo.currentText()
        good_or_service = self.good_service_input.text().strip()
        price_text = self.price_input.text().strip()
        currency = self.currency_combo.currentText()
        expense_date = self.date_input.date().toPyDate()

        if not good_or_service:
            QMessageBox.warning(self, "Input Error", "Please enter a good or service.")
            return
        try:
            price = float(price_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid price.")
            return

        # Convert to USD for consistent storage
        if currency != "USD":
            try:
                converted_price = self.currency_rates.convert(currency, "USD", price, expense_date)
                stored_price = converted_price
            except Exception as e:
                stored_price = price
                QMessageBox.warning(self, "Conversion Error", f"Using original amount (conversion failed: {str(e)})")
        else:
            stored_price = price

        c.execute('''INSERT INTO expenses 
                  (expense_type, good_or_service, price, currency, date) 
                  VALUES (?, ?, ?, ?, ?)''',
                  (expense_type, good_or_service, stored_price, currency,
                   expense_date.strftime('%Y-%m-%d')))
        conn.commit()

        # Clear inputs
        self.good_service_input.clear()
        self.price_input.clear()
        self.load_expenses()
        self.load_summary()
        QMessageBox.information(self, "Success", "Expense added successfully!")

    def init_tab_manage_expenses(self):
        layout = QVBoxLayout(self.tab_manage_expenses)

        # Search and filter
        filter_group = QGroupBox("Search and Filter")
        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search expenses...")
        self.search_input.textChanged.connect(self.load_expenses)
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_input)

        self.category_filter = QComboBox()
        self.category_filter.addItem("ALL CATEGORIES")
        self.category_filter.addItems(self.categories)
        self.category_filter.currentIndexChanged.connect(self.load_expenses)
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.category_filter)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Expense table
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(6)
        self.expense_table.setHorizontalHeaderLabels(["ID", "Type", "Description", "Amount", "Currency", "Date"])
        self.expense_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.expense_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.expense_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.expense_table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected_expense)
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected_expense)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.load_expenses()

    def load_expenses(self):
        search_text = self.search_input.text().strip().lower()
        category_filter = self.category_filter.currentText()

        query = '''SELECT id, expense_type, good_or_service, price, currency, date 
                   FROM expenses'''
        params = []
        
        conditions = []
        if search_text:
            conditions.append('''(LOWER(expense_type) LIKE ? OR 
                               LOWER(good_or_service) LIKE ? OR 
                               LOWER(date) LIKE ?)''')
            like_pattern = f"%{search_text}%"
            params.extend([like_pattern, like_pattern, like_pattern])
        
        if category_filter != "ALL CATEGORIES":
            conditions.append("expense_type = ?")
            params.append(category_filter)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY date DESC"
        
        c.execute(query, params)
        rows = c.fetchall()

        self.expense_table.setRowCount(0)
        for row_data in rows:
            row = self.expense_table.rowCount()
            self.expense_table.insertRow(row)
            
            for col, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                if col in (3,):  # Price column
                    item.setData(Qt.EditRole, float(data))
                self.expense_table.setItem(row, col, item)

        self.expense_table.resizeColumnsToContents()

    def edit_selected_expense(self):
        selected_rows = self.expense_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an expense to edit.")
            return
        
        row = selected_rows[0].row()
        self.edit_expense_by_row(row)

    def edit_expense_by_row(self, row):
        expense_id = int(self.expense_table.item(row, 0).text())
        expense_type = self.expense_table.item(row, 1).text()
        good_or_service = self.expense_table.item(row, 2).text()
        price = self.expense_table.item(row, 3).text()
        currency = self.expense_table.item(row, 4).text()
        date_str = self.expense_table.item(row, 5).text()

        dialog = EditExpenseDialog(expense_id, expense_type, good_or_service, price, 
                                 currency, date_str, self.categories, self)
        if dialog.exec_():
            self.load_expenses()
            self.load_summary()

    def delete_selected_expense(self):
        selected_rows = self.expense_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an expense to delete.")
            return
        
        row = selected_rows[0].row()
        self.delete_expense_by_row(row)

    def delete_expense_by_row(self, row):
        expense_id = int(self.expense_table.item(row, 0).text())
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                    "Are you sure you want to delete this expense?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            
            self.load_expenses()
            self.load_summary()

    def init_tab_summary(self):
        layout = QVBoxLayout(self.tab_summary)

        # Filters
        filter_group = QGroupBox("Summary Filters")
        filter_layout = QHBoxLayout()

        # Category filter
        self.summary_category_combo = QComboBox()
        self.summary_category_combo.addItem("ALL CATEGORIES")
        self.summary_category_combo.addItems(self.categories)
        self.summary_category_combo.currentIndexChanged.connect(self.load_summary)
        filter_layout.addWidget(QLabel("Category:"))
        filter_layout.addWidget(self.summary_category_combo)

        # Date range
        self.summary_start_date = QDateEdit()
        self.summary_start_date.setCalendarPopup(True)
        self.summary_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.summary_start_date.dateChanged.connect(self.load_summary)
        filter_layout.addWidget(QLabel("Start Date:"))
        filter_layout.addWidget(self.summary_start_date)

        self.summary_end_date = QDateEdit()
        self.summary_end_date.setCalendarPopup(True)
        self.summary_end_date.setDate(QDate.currentDate())
        self.summary_end_date.dateChanged.connect(self.load_summary)
        filter_layout.addWidget(QLabel("End Date:"))
        filter_layout.addWidget(self.summary_end_date)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Summary stats
        stats_group = QGroupBox("Statistics")
        stats_layout = QHBoxLayout()

        self.total_label = QLabel("Total: $0.00")
        self.average_label = QLabel("Daily Average: $0.00")
        self.category_label = QLabel("Top Category: None")

        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.average_label)
        stats_layout.addWidget(self.category_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Summary text
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)

        # Plot area
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.load_summary()

    def load_summary(self):
        category = self.summary_category_combo.currentText()
        start_date = self.summary_start_date.date().toPyDate()
        end_date = self.summary_end_date.date().toPyDate()

        # Get filtered data
        query = '''SELECT date, expense_type, SUM(price), currency 
                   FROM expenses 
                   WHERE date BETWEEN ? AND ?'''
        params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
        
        if category != "ALL CATEGORIES":
            query += " AND expense_type = ?"
            params.append(category)
        
        query += " GROUP BY date, expense_type, currency ORDER BY date"
        
        c.execute(query, params)
        rows = c.fetchall()

        # Calculate statistics
        total_query = '''SELECT SUM(price) FROM expenses WHERE date BETWEEN ? AND ?'''
        total_params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
        
        if category != "ALL CATEGORIES":
            total_query += " AND expense_type = ?"
            total_params.append(category)
        
        c.execute(total_query, total_params)
        total = c.fetchone()[0] or 0
        
        days = (end_date - start_date).days + 1
        average = total / days if days > 0 else 0
        
        category_query = '''SELECT expense_type, SUM(price) as total 
                            FROM expenses 
                            WHERE date BETWEEN ? AND ?
                            GROUP BY expense_type 
                            ORDER BY total DESC 
                            LIMIT 1'''
        c.execute(category_query, [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')])
        top_category = c.fetchone()
        
        self.total_label.setText(f"Total: ${total:.2f}")
        self.average_label.setText(f"Daily Average: ${average:.2f}")
        
        if top_category:
            self.category_label.setText(f"Top Category: {top_category[0]} (${top_category[1]:.2f})")
        else:
            self.category_label.setText("Top Category: N/A ($0.00)")

        # Generate detailed summary
        summary_text = f"Expense Summary from {start_date} to {end_date}\n\n"
        daily_totals = {}
        category_totals = {}
        
        for date, expense_type, amount, currency in rows:
            summary_text += f"{date} - {expense_type}: ${amount:.2f} {currency}\n"
            daily_totals.setdefault(date, 0)
            daily_totals[date] += amount
            category_totals.setdefault(expense_type, 0)
            category_totals[expense_type] += amount
        
        summary_text += "\nCategory Breakdown:\n"
        for category, total in category_totals.items():
            summary_text += f"{category}: ${total:.2f}\n"
        
        self.summary_text.setPlainText(summary_text)

        # Update plot
        self.fig.clear()
        
        # Daily spending plot
        ax1 = self.fig.add_subplot(121)
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in daily_totals.keys()]
        totals = list(daily_totals.values())
        ax1.plot(dates, totals, marker='o', linestyle='-', color='b')
        ax1.set_title('Daily Spending')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Amount ($)')
        self.fig.autofmt_xdate()
        
        # Category breakdown pie chart
        ax2 = self.fig.add_subplot(122)
        if category_totals:
            labels = category_totals.keys()
            sizes = category_totals.values()
            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')
            ax2.set_title('Category Breakdown')
        
        self.canvas.draw()

    def init_tab_export(self):
        layout = QVBoxLayout(self.tab_export)

        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout()

        # CSV Export
        csv_group = QGroupBox("CSV Export")
        csv_layout = QVBoxLayout()
        self.csv_btn = QPushButton("Export to CSV")
        self.csv_btn.clicked.connect(self.export_to_csv)
        csv_layout.addWidget(self.csv_btn)
        csv_group.setLayout(csv_layout)
        options_layout.addWidget(csv_group)

        # PDF Export
        pdf_group = QGroupBox("PDF Export")
        pdf_layout = QVBoxLayout()
        self.pdf_btn = QPushButton("Export to PDF")
        self.pdf_btn.clicked.connect(self.export_to_pdf)
        pdf_layout.addWidget(self.pdf_btn)
        pdf_group.setLayout(pdf_layout)
        options_layout.addWidget(pdf_group)

        # Report options
        report_group = QGroupBox("Report Options")
        report_layout = QFormLayout()

        self.report_start_date = QDateEdit()
        self.report_start_date.setCalendarPopup(True)
        self.report_start_date.setDate(QDate.currentDate().addMonths(-1))
        report_layout.addRow(QLabel("Start Date:"), self.report_start_date)

        self.report_end_date = QDateEdit()
        self.report_end_date.setCalendarPopup(True)
        self.report_end_date.setDate(QDate.currentDate())
        report_layout.addRow(QLabel("End Date:"), self.report_end_date)

        self.report_category = QComboBox()
        self.report_category.addItem("ALL CATEGORIES")
        self.report_category.addItems(self.categories)
        report_layout.addRow(QLabel("Category:"), self.report_category)

        report_group.setLayout(report_layout)
        options_layout.addWidget(report_group)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

    def export_to_csv(self):
        start_date = self.report_start_date.date().toPyDate()
        end_date = self.report_end_date.date().toPyDate()
        category = self.report_category.currentText()

        query = '''SELECT date, expense_type, good_or_service, price, currency 
                   FROM expenses 
                   WHERE date BETWEEN ? AND ?'''
        params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
        
        if category != "ALL CATEGORIES":
            query += " AND expense_type = ?"
            params.append(category)
        
        query += " ORDER BY date DESC"
        
        c.execute(query, params)
        rows = c.fetchall()

        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", 
                                                 "expenses_export.csv", "CSV Files (*.csv)")
        
        if file_path:
            try:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Date', 'Category', 'Description', 'Amount', 'Currency'])
                    for row in rows:
                        writer.writerow(row)
                QMessageBox.information(self, "Export Successful", 
                                      f"Expenses exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", 
                                  f"Failed to export CSV: {str(e)}")

    def export_to_pdf(self):
        start_date = self.report_start_date.date().toPyDate()
        end_date = self.report_end_date.date().toPyDate()
        category = self.report_category.currentText()

        query = '''SELECT date, expense_type, good_or_service, price, currency 
                   FROM expenses 
                   WHERE date BETWEEN ? AND ?'''
        params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
        
        if category != "ALL CATEGORIES":
            query += " AND expense_type = ?"
            params.append(category)
        
        query += " ORDER BY date DESC"
        
        c.execute(query, params)
        rows = c.fetchall()

        # Calculate totals
        total_query = '''SELECT SUM(price) FROM expenses WHERE date BETWEEN ? AND ?'''
        total_params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
        
        if category != "ALL CATEGORIES":
            total_query += " AND expense_type = ?"
            total_params.append(category)
        
        c.execute(total_query, total_params)
        total = c.fetchone()[0] or 0

        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF File", 
                                                 "expenses_report.pdf", "PDF Files (*.pdf)")
        
        if file_path:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "Expense Report", ln=True, align='C')
                
                # Report details
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, f"Period: {start_date} to {end_date}", ln=True)
                pdf.cell(0, 10, f"Category: {category}", ln=True)
                pdf.cell(0, 10, f"Total Expenses: ${total:.2f}", ln=True)
                pdf.ln(10)
                
                # Table header
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(40, 10, "Date", border=1)
                pdf.cell(40, 10, "Category", border=1)
                pdf.cell(60, 10, "Description", border=1)
                pdf.cell(25, 10, "Amount", border=1)
                pdf.cell(25, 10, "Currency", border=1, ln=True)
                
                # Table rows
                pdf.set_font("Arial", '', 10)
                for row in rows:
                    pdf.cell(40, 10, row[0])
                    pdf.cell(40, 10, row[1])
                    pdf.cell(60, 10, row[2])
                    pdf.cell(25, 10, f"{row[3]:.2f}", align='R')
                    pdf.cell(25, 10, row[4], ln=True)
                
                pdf.output(file_path)
                QMessageBox.information(self, "Export Successful", 
                                      f"Report exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", 
                                  f"Failed to export PDF: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ExpenseTracker()
    window.show()
    sys.exit(app.exec_())