"""
gui/invoices.py

Invoice Management page for CulinaryOps Central.
"""

import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from database.invoices import (
    add_invoice,
    delete_invoice,
    get_all_invoices,
    get_vendor_options,
    search_invoices,
    update_invoice,
)
from gui.base_crud_page import BaseCrudPage


class InvoicesPage(BaseCrudPage):
    """
    Invoice Management page.

    Allows the user to:
    - View invoices
    - Search invoices
    - Add invoices
    - Edit invoices
    - Delete invoices
    """

    def __init__(
        self,
        parent,
        status_callback=None,
        dashboard_callback=None,
    ):
        super().__init__(
            parent,
            title="Invoice Management",
            description="Add, update, search, and manage vendor invoices.",
        )

        self.status_callback = status_callback
        self.dashboard_callback = dashboard_callback

        self.selected_invoice_id = None
        self.vendor_lookup = {}
        self.vendor_name_lookup = {}

        self.create_form_section()
        self.create_search_section()
        self.create_table_section()

        self.load_vendors()
        self.load_invoices()

    # ---------------------------------------------------------
    # FORM SECTION
    # ---------------------------------------------------------

    def create_form_section(self):
        form_card = ctk.CTkFrame(self, corner_radius=12)
        form_card.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=15,
            pady=(0, 10),
        )

        for column in range(4):
            form_card.grid_columnconfigure(column, weight=1)

        form_title = ctk.CTkLabel(
            form_card,
            text="Invoice Information",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        form_title.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            padx=20,
            pady=(15, 10),
        )

        labels = [
            "Vendor *",
            "Invoice Date *",
            "Amount *",
            "Status",
        ]

        for column, label_text in enumerate(labels):
            ctk.CTkLabel(
                form_card,
                text=label_text,
                anchor="w",
            ).grid(
                row=1,
                column=column,
                sticky="w",
                padx=(20 if column == 0 else 10, 20 if column == 3 else 10),
                pady=(5, 2),
            )

        self.vendor_box = ctk.CTkComboBox(
            form_card,
            values=["No vendors available"],
            height=38,
            state="readonly",
        )
        self.invoice_date_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="YYYY-MM-DD",
            height=38,
        )
        self.amount_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Example: 1250.00",
            height=38,
        )
        self.status_box = ctk.CTkComboBox(
            form_card,
            values=["Pending", "Paid"],
            height=38,
            state="readonly",
        )
        self.status_box.set("Pending")

        fields = [
            self.vendor_box,
            self.invoice_date_entry,
            self.amount_entry,
            self.status_box,
        ]

        for column, field in enumerate(fields):
            field.grid(
                row=2,
                column=column,
                sticky="ew",
                padx=(20 if column == 0 else 10, 20 if column == 3 else 10),
                pady=(0, 10),
            )

        button_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        button_frame.grid(
            row=3,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=20,
            pady=(5, 18),
        )

        self.add_button = ctk.CTkButton(
            button_frame,
            text="Add Invoice",
            width=125,
            height=38,
            command=self.handle_add_invoice,
        )
        self.add_button.pack(side="left", padx=(0, 8))

        self.update_button = ctk.CTkButton(
            button_frame,
            text="Update Invoice",
            width=140,
            height=38,
            state="disabled",
            command=self.handle_update_invoice,
        )
        self.update_button.pack(side="left", padx=8)

        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Clear Form",
            width=110,
            height=38,
            fg_color="gray45",
            hover_color="gray35",
            command=self.clear_form,
        )
        self.clear_button.pack(side="left", padx=8)

        self.delete_button = ctk.CTkButton(
            button_frame,
            text="Delete Invoice",
            width=135,
            height=38,
            fg_color="#B3261E",
            hover_color="#8C1D18",
            state="disabled",
            command=self.handle_delete_invoice,
        )
        self.delete_button.pack(side="right")

    # ---------------------------------------------------------
    # SEARCH SECTION
    # ---------------------------------------------------------

    def create_search_section(self):
        search_frame = ctk.CTkFrame(self, corner_radius=12)
        search_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=15,
            pady=(0, 10),
        )

        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            search_frame,
            text="Search Invoices",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(
            row=0,
            column=0,
            padx=(18, 10),
            pady=15,
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=(
                "Search by vendor, date, amount, status, or invoice ID..."
            ),
            height=38,
        )
        self.search_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=10,
            pady=15,
        )
        self.search_entry.bind("<KeyRelease>", self.handle_live_search)

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=90,
            height=38,
            command=self.handle_search,
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            search_frame,
            text="Show All",
            width=90,
            height=38,
            fg_color="gray45",
            hover_color="gray35",
            command=self.show_all_invoices,
        ).grid(
            row=0,
            column=3,
            padx=(5, 18),
            pady=15,
        )

    # ---------------------------------------------------------
    # TABLE SECTION
    # ---------------------------------------------------------

    def create_table_section(self):
        table_card = ctk.CTkFrame(self, corner_radius=12)
        table_card.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=15,
            pady=(0, 15),
        )

        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(1, weight=1)

        table_header = ctk.CTkFrame(table_card, fg_color="transparent")
        table_header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=18,
            pady=(15, 8),
        )
        table_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            table_header,
            text="Current Invoices",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.invoice_count_label = ctk.CTkLabel(
            table_header,
            text="0 invoices",
            text_color="gray60",
        )
        self.invoice_count_label.grid(row=0, column=1, sticky="e")

        table_container = tk.Frame(table_card, bg="#2B2B2B")
        table_container.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=18,
            pady=(0, 18),
        )
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        self.configure_table_style()

        columns = (
            "invoice_id",
            "vendor",
            "invoice_date",
            "amount",
            "status",
        )

        self.invoice_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Invoice.Treeview",
        )

        headings = {
            "invoice_id": "Invoice ID",
            "vendor": "Vendor",
            "invoice_date": "Invoice Date",
            "amount": "Amount",
            "status": "Status",
        }

        for column_name, heading_text in headings.items():
            self.invoice_table.heading(column_name, text=heading_text)

        self.invoice_table.column(
            "invoice_id",
            width=90,
            minwidth=75,
            anchor="center",
            stretch=False,
        )
        self.invoice_table.column(
            "vendor",
            width=260,
            minwidth=170,
            anchor="w",
        )
        self.invoice_table.column(
            "invoice_date",
            width=130,
            minwidth=110,
            anchor="center",
        )
        self.invoice_table.column(
            "amount",
            width=130,
            minwidth=100,
            anchor="e",
        )
        self.invoice_table.column(
            "status",
            width=120,
            minwidth=100,
            anchor="center",
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.invoice_table.yview,
        )
        horizontal_scrollbar = ttk.Scrollbar(
            table_container,
            orient="horizontal",
            command=self.invoice_table.xview,
        )

        self.invoice_table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.invoice_table.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.invoice_table.bind(
            "<<TreeviewSelect>>",
            self.handle_table_selection,
        )
        self.invoice_table.bind(
            "<Double-1>",
            self.handle_table_double_click,
        )

    def configure_table_style(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Invoice.Treeview",
            background="#FFFFFF",
            foreground="#1F1F1F",
            fieldbackground="#FFFFFF",
            rowheight=34,
            borderwidth=0,
            font=("Arial", 12),
        )
        style.configure(
            "Invoice.Treeview.Heading",
            background="#1F6AA5",
            foreground="#FFFFFF",
            relief="flat",
            font=("Arial", 12, "bold"),
            padding=(8, 8),
        )
        style.map(
            "Invoice.Treeview",
            background=[("selected", "#3B8ED0")],
            foreground=[("selected", "#FFFFFF")],
        )
        style.map(
            "Invoice.Treeview.Heading",
            background=[("active", "#175A8C")],
        )

    # ---------------------------------------------------------
    # DATABASE AND TABLE FUNCTIONS
    # ---------------------------------------------------------

    def load_vendors(self):
        try:
            vendors = get_vendor_options()

            self.vendor_lookup.clear()
            self.vendor_name_lookup.clear()

            for vendor in vendors:
                vendor_id = vendor[0]
                vendor_name = vendor[1]

                self.vendor_lookup[vendor_name] = vendor_id
                self.vendor_name_lookup[vendor_id] = vendor_name

            vendor_names = list(self.vendor_lookup.keys())

            if vendor_names:
                self.vendor_box.configure(values=vendor_names)
                self.vendor_box.set(vendor_names[0])
                self.add_button.configure(state="normal")
            else:
                self.vendor_box.configure(values=["No vendors available"])
                self.vendor_box.set("No vendors available")
                self.add_button.configure(state="disabled")
                self.update_status(
                    "Add a vendor before creating an invoice."
                )

        except Exception as error:
            messagebox.showerror(
                "Vendor Error",
                f"Unable to load vendor options.\n\n{error}",
            )
            self.update_status("Unable to load vendor options.")

    def load_invoices(self, invoices=None):
        try:
            if invoices is None:
                invoices = get_all_invoices()

            self.clear_table()

            for invoice in invoices:
                invoice_id = self.get_invoice_value(
                    invoice,
                    "invoiceID",
                    0,
                )
                vendor_name = self.get_invoice_value(
                    invoice,
                    "vendorName",
                    1,
                )
                invoice_date = self.get_invoice_value(
                    invoice,
                    "invoiceDate",
                    2,
                )
                amount = self.get_invoice_value(
                    invoice,
                    "amount",
                    3,
                )
                status = self.get_invoice_value(
                    invoice,
                    "status",
                    4,
                )

                try:
                    amount_display = f"${float(amount):,.2f}"
                except (TypeError, ValueError):
                    amount_display = str(amount or "")

                self.invoice_table.insert(
                    "",
                    "end",
                    values=(
                        invoice_id,
                        vendor_name or "",
                        invoice_date or "",
                        amount_display,
                        status or "",
                    ),
                )

            total = len(invoices)
            self.invoice_count_label.configure(
                text=f"{total} invoice" if total == 1 else f"{total} invoices"
            )

        except Exception as error:
            messagebox.showerror(
                "Invoice Error",
                f"Unable to load invoices.\n\n{error}",
            )
            self.update_status("Unable to load invoice records.")

    @staticmethod
    def get_invoice_value(invoice, key, index):
        """
        Supports both sqlite3.Row/dictionary records and tuple records.
        """

        try:
            return invoice[key]
        except (TypeError, KeyError, IndexError):
            return invoice[index]

    def clear_table(self):
        for item in self.invoice_table.get_children():
            self.invoice_table.delete(item)

    # ---------------------------------------------------------
    # ADD, UPDATE, DELETE
    # ---------------------------------------------------------

    def handle_add_invoice(self):
        vendor_id = self.get_selected_vendor_id()

        if vendor_id is None:
            messagebox.showwarning(
                "Vendor Required",
                "Select a valid vendor before adding an invoice.",
            )
            return

        try:
            invoice_id = add_invoice(
                vendor_id,
                self.invoice_date_entry.get(),
                self.amount_entry.get(),
                self.status_box.get(),
            )

            messagebox.showinfo(
                "Invoice Added",
                f"Invoice #{invoice_id} added successfully.",
            )
            self.clear_form()
            self.load_invoices()
            self.refresh_dashboard()
            self.update_status("Invoice added successfully.")

        except (ValueError, TypeError) as error:
            messagebox.showwarning("Unable to Add Invoice", str(error))
            self.update_status("Invoice was not added.")
        except Exception as error:
            messagebox.showerror(
                "Invoice Error",
                f"Unable to add invoice.\n\n{error}",
            )
            self.update_status("Invoice was not added.")

    def handle_update_invoice(self):
        if self.selected_invoice_id is None:
            messagebox.showwarning(
                "No Invoice Selected",
                "Select an invoice from the table first.",
            )
            return

        vendor_id = self.get_selected_vendor_id()

        if vendor_id is None:
            messagebox.showwarning(
                "Vendor Required",
                "Select a valid vendor before updating the invoice.",
            )
            return

        try:
            updated = update_invoice(
                self.selected_invoice_id,
                vendor_id,
                self.invoice_date_entry.get(),
                self.amount_entry.get(),
                self.status_box.get(),
            )

            if not updated:
                messagebox.showwarning(
                    "Unable to Update Invoice",
                    "Invoice was not found.",
                )
                self.update_status("Invoice was not updated.")
                return

            messagebox.showinfo(
                "Invoice Updated",
                "Invoice updated successfully.",
            )
            self.clear_form()
            self.load_invoices()
            self.refresh_dashboard()
            self.update_status("Invoice updated successfully.")

        except (ValueError, TypeError) as error:
            messagebox.showwarning("Unable to Update Invoice", str(error))
            self.update_status("Invoice was not updated.")
        except Exception as error:
            messagebox.showerror(
                "Invoice Error",
                f"Unable to update invoice.\n\n{error}",
            )
            self.update_status("Invoice was not updated.")

    def handle_delete_invoice(self):
        if self.selected_invoice_id is None:
            messagebox.showwarning(
                "No Invoice Selected",
                "Select an invoice from the table first.",
            )
            return

        vendor_name = self.vendor_box.get().strip()

        confirmation = messagebox.askyesno(
            "Delete Invoice",
            (
                f"Are you sure you want to delete invoice "
                f"#{self.selected_invoice_id} for '{vendor_name}'?\n\n"
                "This action cannot be undone."
            ),
        )

        if not confirmation:
            self.update_status("Invoice deletion canceled.")
            return

        try:
            deleted = delete_invoice(self.selected_invoice_id)

            if not deleted:
                messagebox.showwarning(
                    "Unable to Delete Invoice",
                    "Invoice was not found.",
                )
                self.update_status("Invoice was not deleted.")
                return

            messagebox.showinfo(
                "Invoice Deleted",
                "Invoice deleted successfully.",
            )
            self.clear_form()
            self.load_invoices()
            self.refresh_dashboard()
            self.update_status("Invoice deleted successfully.")

        except Exception as error:
            messagebox.showerror(
                "Invoice Error",
                f"Unable to delete invoice.\n\n{error}",
            )
            self.update_status("Invoice was not deleted.")

    # ---------------------------------------------------------
    # SEARCH FUNCTIONS
    # ---------------------------------------------------------

    def handle_search(self):
        keyword = self.search_entry.get()

        try:
            invoices = search_invoices(keyword)
            self.load_invoices(invoices)

            if keyword.strip():
                self.update_status(
                    f"Invoice search completed for '{keyword.strip()}'."
                )
            else:
                self.update_status("All invoice records displayed.")

        except Exception as error:
            messagebox.showerror(
                "Search Error",
                f"Unable to search invoices.\n\n{error}",
            )

    def handle_live_search(self, event=None):
        try:
            self.load_invoices(search_invoices(self.search_entry.get()))
        except Exception:
            pass

    def show_all_invoices(self):
        self.search_entry.delete(0, "end")
        self.load_invoices()
        self.update_status("All invoice records displayed.")

    # ---------------------------------------------------------
    # TABLE SELECTION
    # ---------------------------------------------------------

    def handle_table_selection(self, event=None):
        selected_items = self.invoice_table.selection()

        if not selected_items:
            return

        values = self.invoice_table.item(
            selected_items[0],
            "values",
        )

        if not values:
            return

        self.selected_invoice_id = int(values[0])

        vendor_name = values[1]
        invoice_date = values[2]
        amount = str(values[3]).replace("$", "").replace(",", "")
        status = values[4]

        if vendor_name in self.vendor_lookup:
            self.vendor_box.set(vendor_name)

        self.invoice_date_entry.delete(0, "end")
        self.invoice_date_entry.insert(0, invoice_date)

        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, amount)

        if status in self.status_box.cget("values"):
            self.status_box.set(status)
        else:
            self.status_box.set("Pending")

        self.add_button.configure(state="disabled")
        self.update_button.configure(state="normal")
        self.delete_button.configure(state="normal")

        self.update_status(
            f"Invoice selected: #{self.selected_invoice_id}"
        )

    def handle_table_double_click(self, event=None):
        self.handle_table_selection()
        self.invoice_date_entry.focus_set()

    # ---------------------------------------------------------
    # FORM UTILITIES
    # ---------------------------------------------------------

    def get_selected_vendor_id(self):
        vendor_name = self.vendor_box.get().strip()
        return self.vendor_lookup.get(vendor_name)

    def clear_form(self):
        self.selected_invoice_id = None

        self.invoice_date_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")
        self.status_box.set("Pending")

        vendor_names = list(self.vendor_lookup.keys())

        if vendor_names:
            self.vendor_box.set(vendor_names[0])
            self.add_button.configure(state="normal")
        else:
            self.vendor_box.set("No vendors available")
            self.add_button.configure(state="disabled")

        for item in self.invoice_table.selection():
            self.invoice_table.selection_remove(item)

        self.update_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")

        self.invoice_date_entry.focus_set()
        self.update_status("Invoice form cleared.")

    # ---------------------------------------------------------
    # CALLBACKS TO MAIN APPLICATION
    # ---------------------------------------------------------

    def update_status(self, message):
        if callable(self.status_callback):
            self.status_callback(message)

    def refresh_dashboard(self):
        if callable(self.dashboard_callback):
            self.dashboard_callback()