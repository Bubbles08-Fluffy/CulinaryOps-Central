import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from database.sales import (
    add_sale,
    delete_sale,
    get_all_sales,
    search_sales,
    update_sale,
)
from gui.base_crud_page import BaseCrudPage


class SalesPage(BaseCrudPage):
    """
    Sales Records page.

    Allows the user to:
    - View sales records
    - Search sales records
    - Add sales records
    - Edit sales records
    - Delete sales records
    """

    def __init__(
        self,
        parent,
        status_callback=None,
        dashboard_callback=None,
    ):
        super().__init__(
            parent,
            title="Sales Records",
            description="Track daily meals sold and total dining service revenue.",
        )

        self.status_callback = status_callback
        self.dashboard_callback = dashboard_callback
        self.selected_sales_id = None

        self.create_form_section()
        self.create_search_section()
        self.create_table_section()

        self.load_sales()

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

        for column in range(3):
            form_card.grid_columnconfigure(column, weight=1)

        ctk.CTkLabel(
            form_card,
            text="Sales Information",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=20,
            pady=(15, 10),
        )

        labels = [
            "Sale Date *",
            "Meals Sold *",
            "Total Revenue *",
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
                padx=(20 if column == 0 else 10, 20 if column == 2 else 10),
                pady=(5, 2),
            )

        self.sales_date_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="YYYY-MM-DD",
            height=38,
        )
        self.meals_sold_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Example: 425",
            height=38,
        )
        self.total_revenue_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Example: 2845.50",
            height=38,
        )

        entries = [
            self.sales_date_entry,
            self.meals_sold_entry,
            self.total_revenue_entry,
        ]

        for column, entry in enumerate(entries):
            entry.grid(
                row=2,
                column=column,
                sticky="ew",
                padx=(20 if column == 0 else 10, 20 if column == 2 else 10),
                pady=(0, 10),
            )

        button_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        button_frame.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=20,
            pady=(5, 18),
        )

        self.add_button = ctk.CTkButton(
            button_frame,
            text="Add Sale",
            width=120,
            height=38,
            command=self.handle_add_sale,
        )
        self.add_button.pack(side="left", padx=(0, 8))

        self.update_button = ctk.CTkButton(
            button_frame,
            text="Update Sale",
            width=130,
            height=38,
            state="disabled",
            command=self.handle_update_sale,
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
            text="Delete Sale",
            width=130,
            height=38,
            fg_color="#B3261E",
            hover_color="#8C1D18",
            state="disabled",
            command=self.handle_delete_sale,
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
            text="Search Sales",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(
            row=0,
            column=0,
            padx=(18, 10),
            pady=15,
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by ID, date, meals sold, or revenue...",
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
            command=self.show_all_sales,
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
            text="Current Sales Records",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.sales_count_label = ctk.CTkLabel(
            table_header,
            text="0 sales records",
            text_color="gray60",
        )
        self.sales_count_label.grid(row=0, column=1, sticky="e")

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
            "sales_id",
            "sales_date",
            "meals_sold",
            "total_revenue",
        )

        self.sales_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Sales.Treeview",
        )

        headings = {
            "sales_id": "ID",
            "sales_date": "Sale Date",
            "meals_sold": "Meals Sold",
            "total_revenue": "Total Revenue",
        }

        for column_name, heading_text in headings.items():
            self.sales_table.heading(column_name, text=heading_text)

        self.sales_table.column(
            "sales_id",
            width=70,
            minwidth=55,
            anchor="center",
            stretch=False,
        )
        self.sales_table.column(
            "sales_date",
            width=180,
            minwidth=140,
            anchor="center",
        )
        self.sales_table.column(
            "meals_sold",
            width=180,
            minwidth=140,
            anchor="center",
        )
        self.sales_table.column(
            "total_revenue",
            width=220,
            minwidth=160,
            anchor="e",
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.sales_table.yview,
        )
        horizontal_scrollbar = ttk.Scrollbar(
            table_container,
            orient="horizontal",
            command=self.sales_table.xview,
        )

        self.sales_table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.sales_table.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.sales_table.bind(
            "<<TreeviewSelect>>",
            self.handle_table_selection,
        )
        self.sales_table.bind(
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
            "Sales.Treeview",
            background="#FFFFFF",
            foreground="#1F1F1F",
            fieldbackground="#FFFFFF",
            rowheight=34,
            borderwidth=0,
            font=("Arial", 12),
        )
        style.configure(
            "Sales.Treeview.Heading",
            background="#1F6AA5",
            foreground="#FFFFFF",
            relief="flat",
            font=("Arial", 12, "bold"),
            padding=(8, 8),
        )
        style.map(
            "Sales.Treeview",
            background=[("selected", "#3B8ED0")],
            foreground=[("selected", "#FFFFFF")],
        )
        style.map(
            "Sales.Treeview.Heading",
            background=[("active", "#175A8C")],
        )

    # ---------------------------------------------------------
    # DATABASE AND TABLE FUNCTIONS
    # ---------------------------------------------------------

    def load_sales(self, sales_records=None):
        try:
            if sales_records is None:
                sales_records = get_all_sales()

            self.clear_table()

            for sale in sales_records:
                revenue = float(sale[3] or 0)
                self.sales_table.insert(
                    "",
                    "end",
                    values=(
                        sale[0],
                        sale[1] or "",
                        sale[2] or 0,
                        f"${revenue:,.2f}",
                    ),
                )

            total = len(sales_records)
            self.sales_count_label.configure(
                text=(
                    f"{total} sales record"
                    if total == 1
                    else f"{total} sales records"
                )
            )

        except Exception as error:
            messagebox.showerror(
                "Sales Error",
                f"Unable to load sales records.\n\n{error}",
            )
            self.update_status("Unable to load sales records.")

    def clear_table(self):
        for item in self.sales_table.get_children():
            self.sales_table.delete(item)

    # ---------------------------------------------------------
    # ADD, UPDATE, DELETE
    # ---------------------------------------------------------

    def handle_add_sale(self):
        sale_id = add_sale(
            self.sales_date_entry.get(),
            self.meals_sold_entry.get(),
            self.total_revenue_entry.get(),
        )

        if sale_id:
            messagebox.showinfo("Sale Added", "Sales record added successfully.")
            self.clear_form()
            self.load_sales()
            self.refresh_dashboard()
        else:
            messagebox.showwarning("Unable to Add Sale", "Sales record was not added.")

    def handle_update_sale(self):
        if self.selected_sales_id is None:
            messagebox.showwarning(
                "No Sale Selected",
                "Select a sales record from the table first.",
            )
            return

        success = update_sale(
            self.selected_sales_id,
            self.sales_date_entry.get(),
            self.meals_sold_entry.get(),
            self.total_revenue_entry.get(),
        )

        if success:
            messagebox.showinfo("Sale Updated", "Sales record updated successfully.")
            self.clear_form()
            self.load_sales()
            self.refresh_dashboard()
        else:
            messagebox.showwarning("Unable to Update Sale", "Sales record was not updated.")

    def handle_delete_sale(self):
        if self.selected_sales_id is None:
            messagebox.showwarning(
                "No Sale Selected",
                "Select a sales record from the table first.",
            )
            return

        confirmation = messagebox.askyesno(
            "Delete Sale",
            (
                "Are you sure you want to delete the selected sales record?\n\n"
                "This action cannot be undone."
            ),
        )

        if not confirmation:
            self.update_status("Sales record deletion canceled.")
            return

        success = delete_sale(self.selected_sales_id)

        if success:
            messagebox.showinfo("Sale Deleted", "Sales record deleted successfully.")
            self.clear_form()
            self.load_sales()
            self.refresh_dashboard()
        else:
            messagebox.showwarning("Unable to Delete Sale", "Sales record was not deleted.")

    # ---------------------------------------------------------
    # SEARCH FUNCTIONS
    # ---------------------------------------------------------

    def handle_search(self):
        keyword = self.search_entry.get().strip()

        try:
            results = search_sales(keyword)
            self.load_sales(results)
            self.clear_selection()

            if keyword:
                self.update_status(
                    f"Sales search completed: {len(results)} result(s)."
                )
            else:
                self.update_status("All sales records displayed.")

        except Exception as error:
            messagebox.showerror(
                "Search Error",
                f"Unable to search sales records.\n\n{error}",
            )
            self.update_status("Unable to search sales records.")

    def handle_live_search(self, _event=None):
        self.handle_search()

    def show_all_sales(self):
        self.search_entry.delete(0, "end")
        self.load_sales()
        self.clear_selection()
        self.update_status("All sales records displayed.")

    # ---------------------------------------------------------
    # TABLE SELECTION
    # ---------------------------------------------------------

    def handle_table_selection(self, _event=None):
        selected_items = self.sales_table.selection()

        if not selected_items:
            return

        selected_item = selected_items[0]
        raw_values = self.sales_table.item(selected_item, "values")

        if not isinstance(raw_values, (tuple, list)) or len(raw_values) < 4:
            return

        values = tuple(raw_values)

        try:
            self.selected_sales_id = int(values[0])
        except (TypeError, ValueError):
            self.selected_sales_id = None
            return

        self.sales_date_entry.delete(0, "end")
        self.sales_date_entry.insert(0, str(values[1]))

        self.meals_sold_entry.delete(0, "end")
        self.meals_sold_entry.insert(0, str(values[2]))

        revenue_text = str(values[3]).replace("$", "").replace(",", "")
        self.total_revenue_entry.delete(0, "end")
        self.total_revenue_entry.insert(0, revenue_text)

        self.update_button.configure(state="normal")
        self.delete_button.configure(state="normal")
        self.update_status(
            f"Sales record {self.selected_sales_id} selected."
        )

    def handle_table_double_click(self, _event=None):
        self.handle_table_selection()

    # ---------------------------------------------------------
    # FORM UTILITIES
    # ---------------------------------------------------------

    def clear_form(self):
        self.sales_date_entry.delete(0, "end")
        self.meals_sold_entry.delete(0, "end")
        self.total_revenue_entry.delete(0, "end")

        self.selected_sales_id = None
        self.clear_selection()

        self.update_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")

        self.sales_date_entry.focus_set()
        self.update_status("Sales form cleared.")

    def clear_selection(self):
        for item in self.sales_table.selection():
            self.sales_table.selection_remove(item)

        self.selected_sales_id = None
        self.update_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")

    # ---------------------------------------------------------
    # CALLBACK HELPERS
    # ---------------------------------------------------------

    def update_status(self, message):
        if callable(self.status_callback):
            self.status_callback(message)

    def refresh_dashboard(self):
        if callable(self.dashboard_callback):
            self.dashboard_callback()
