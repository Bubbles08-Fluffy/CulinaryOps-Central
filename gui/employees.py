import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from database.employees import (
    add_employee,
    delete_employee,
    get_all_employees,
    search_employees,
    update_employee,
)
from gui.base_crud_page import BaseCrudPage


class EmployeesPage(BaseCrudPage):
    """
    Employee Management page.

    Allows the user to:
    - View employees
    - Search employees
    - Add employees
    - Edit employees
    - Delete employees
    """

    def __init__(
        self,
        parent,
        status_callback=None,
        dashboard_callback=None,
    ):
        super().__init__(
            parent,
            title="Employee Management",
            description="Add, update, search, and manage dining service employees.",
        )

        self.status_callback = status_callback
        self.dashboard_callback = dashboard_callback
        self.selected_employee_id = None

        self.create_form_section()
        self.create_search_section()
        self.create_table_section()

        self.load_employees()

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

        for column in range(5):
            form_card.grid_columnconfigure(column, weight=1)

        form_title = ctk.CTkLabel(
            form_card,
            text="Employee Information",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        form_title.grid(
            row=0,
            column=0,
            columnspan=5,
            sticky="w",
            padx=20,
            pady=(15, 10),
        )

        labels = [
            "First Name *",
            "Last Name *",
            "Position",
            "Hire Date",
            "Phone Number",
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
                padx=(20 if column == 0 else 10, 20 if column == 4 else 10),
                pady=(5, 2),
            )

        self.first_name_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="First name",
            height=38,
        )
        self.last_name_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Last name",
            height=38,
        )
        self.position_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="Example: Supervisor",
            height=38,
        )
        self.hire_date_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="YYYY-MM-DD",
            height=38,
        )
        self.phone_number_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="334-555-0000",
            height=38,
        )

        entries = [
            self.first_name_entry,
            self.last_name_entry,
            self.position_entry,
            self.hire_date_entry,
            self.phone_number_entry,
        ]

        for column, entry in enumerate(entries):
            entry.grid(
                row=2,
                column=column,
                sticky="ew",
                padx=(20 if column == 0 else 10, 20 if column == 4 else 10),
                pady=(0, 10),
            )

        button_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        button_frame.grid(
            row=3,
            column=0,
            columnspan=5,
            sticky="ew",
            padx=20,
            pady=(5, 18),
        )

        self.add_button = ctk.CTkButton(
            button_frame,
            text="Add Employee",
            width=135,
            height=38,
            command=self.handle_add_employee,
        )
        self.add_button.pack(side="left", padx=(0, 8))

        self.update_button = ctk.CTkButton(
            button_frame,
            text="Update Employee",
            width=145,
            height=38,
            state="disabled",
            command=self.handle_update_employee,
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
            text="Delete Employee",
            width=145,
            height=38,
            fg_color="#B3261E",
            hover_color="#8C1D18",
            state="disabled",
            command=self.handle_delete_employee,
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
            text="Search Employees",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(
            row=0,
            column=0,
            padx=(18, 10),
            pady=15,
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by name, position, hire date, or phone...",
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
            command=self.show_all_employees,
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
            text="Current Employees",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.employee_count_label = ctk.CTkLabel(
            table_header,
            text="0 employees",
            text_color="gray60",
        )
        self.employee_count_label.grid(row=0, column=1, sticky="e")

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
            "employee_id",
            "first_name",
            "last_name",
            "position",
            "hire_date",
            "phone_number",
        )

        self.employee_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Employee.Treeview",
        )

        headings = {
            "employee_id": "ID",
            "first_name": "First Name",
            "last_name": "Last Name",
            "position": "Position",
            "hire_date": "Hire Date",
            "phone_number": "Phone Number",
        }

        for column_name, heading_text in headings.items():
            self.employee_table.heading(column_name, text=heading_text)

        self.employee_table.column(
            "employee_id",
            width=55,
            minwidth=45,
            anchor="center",
            stretch=False,
        )
        self.employee_table.column(
            "first_name",
            width=140,
            minwidth=110,
            anchor="w",
        )
        self.employee_table.column(
            "last_name",
            width=140,
            minwidth=110,
            anchor="w",
        )
        self.employee_table.column(
            "position",
            width=190,
            minwidth=140,
            anchor="w",
        )
        self.employee_table.column(
            "hire_date",
            width=115,
            minwidth=100,
            anchor="center",
        )
        self.employee_table.column(
            "phone_number",
            width=145,
            minwidth=120,
            anchor="center",
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.employee_table.yview,
        )
        horizontal_scrollbar = ttk.Scrollbar(
            table_container,
            orient="horizontal",
            command=self.employee_table.xview,
        )

        self.employee_table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.employee_table.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.employee_table.bind(
            "<<TreeviewSelect>>",
            self.handle_table_selection,
        )
        self.employee_table.bind(
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
            "Employee.Treeview",
            background="#FFFFFF",
            foreground="#1F1F1F",
            fieldbackground="#FFFFFF",
            rowheight=34,
            borderwidth=0,
            font=("Arial", 12),
        )
        style.configure(
            "Employee.Treeview.Heading",
            background="#1F6AA5",
            foreground="#FFFFFF",
            relief="flat",
            font=("Arial", 12, "bold"),
            padding=(8, 8),
        )
        style.map(
            "Employee.Treeview",
            background=[("selected", "#3B8ED0")],
            foreground=[("selected", "#FFFFFF")],
        )
        style.map(
            "Employee.Treeview.Heading",
            background=[("active", "#175A8C")],
        )

    # ---------------------------------------------------------
    # DATABASE AND TABLE FUNCTIONS
    # ---------------------------------------------------------

    def load_employees(self, employees=None):
        try:
            if employees is None:
                employees = get_all_employees()

            self.clear_table()

            for employee in employees:
                self.employee_table.insert(
                    "",
                    "end",
                    values=(
                        employee[0],
                        employee[1] or "",
                        employee[2] or "",
                        employee[3] or "",
                        employee[4] or "",
                        employee[5] or "",
                    ),
                )

            total = len(employees)
            self.employee_count_label.configure(
                text=f"{total} employee" if total == 1 else f"{total} employees"
            )

        except Exception as error:
            messagebox.showerror(
                "Employee Error",
                f"Unable to load employees.\n\n{error}",
            )
            self.update_status("Unable to load employee records.")

    def clear_table(self):
        for item in self.employee_table.get_children():
            self.employee_table.delete(item)

    # ---------------------------------------------------------
    # ADD, UPDATE, DELETE
    # ---------------------------------------------------------

    def handle_add_employee(self):
        success, message = add_employee(
            self.first_name_entry.get(),
            self.last_name_entry.get(),
            self.position_entry.get(),
            self.hire_date_entry.get(),
            self.phone_number_entry.get(),
        )

        if success:
            messagebox.showinfo("Employee Added", message)
            self.clear_form()
            self.load_employees()
            self.refresh_dashboard()
            self.update_status("Employee added successfully.")
        else:
            messagebox.showwarning("Unable to Add Employee", message)
            self.update_status("Employee was not added.")

    def handle_update_employee(self):
        if self.selected_employee_id is None:
            messagebox.showwarning(
                "No Employee Selected",
                "Select an employee from the table first.",
            )
            return

        success, message = update_employee(
            self.selected_employee_id,
            self.first_name_entry.get(),
            self.last_name_entry.get(),
            self.position_entry.get(),
            self.hire_date_entry.get(),
            self.phone_number_entry.get(),
        )

        if success:
            messagebox.showinfo("Employee Updated", message)
            self.clear_form()
            self.load_employees()
            self.refresh_dashboard()
            self.update_status("Employee updated successfully.")
        else:
            messagebox.showwarning("Unable to Update Employee", message)
            self.update_status("Employee was not updated.")

    def handle_delete_employee(self):
        if self.selected_employee_id is None:
            messagebox.showwarning(
                "No Employee Selected",
                "Select an employee from the table first.",
            )
            return

        full_name = (
            f"{self.first_name_entry.get().strip()} "
            f"{self.last_name_entry.get().strip()}"
        ).strip()

        confirmation = messagebox.askyesno(
            "Delete Employee",
            (
                f"Are you sure you want to delete '{full_name}'?\n\n"
                "This action cannot be undone."
            ),
        )

        if not confirmation:
            self.update_status("Employee deletion canceled.")
            return

        success, message = delete_employee(self.selected_employee_id)

        if success:
            messagebox.showinfo("Employee Deleted", message)
            self.clear_form()
            self.load_employees()
            self.refresh_dashboard()
            self.update_status("Employee deleted successfully.")
        else:
            messagebox.showwarning("Unable to Delete Employee", message)
            self.update_status("Employee was not deleted.")

    # ---------------------------------------------------------
    # SEARCH FUNCTIONS
    # ---------------------------------------------------------

    def handle_search(self):
        keyword = self.search_entry.get()

        try:
            employees = search_employees(keyword)
            self.load_employees(employees)

            if keyword.strip():
                self.update_status(
                    f"Employee search completed for '{keyword.strip()}'."
                )
            else:
                self.update_status("All employee records displayed.")

        except Exception as error:
            messagebox.showerror(
                "Search Error",
                f"Unable to search employees.\n\n{error}",
            )

    def handle_live_search(self, event=None):
        try:
            self.load_employees(search_employees(self.search_entry.get()))
        except Exception:
            pass

    def show_all_employees(self):
        self.search_entry.delete(0, "end")
        self.load_employees()
        self.update_status("All employee records displayed.")

    # ---------------------------------------------------------
    # TABLE SELECTION
    # ---------------------------------------------------------

    def handle_table_selection(self, event=None):
        selected_items = self.employee_table.selection()

        if not selected_items:
            return

        values = self.employee_table.item(
            selected_items[0],
            "values",
        )

        if not values:
            return

        self.selected_employee_id = int(values[0])

        entries_and_values = [
            (self.first_name_entry, values[1]),
            (self.last_name_entry, values[2]),
            (self.position_entry, values[3]),
            (self.hire_date_entry, values[4]),
            (self.phone_number_entry, values[5]),
        ]

        for entry, value in entries_and_values:
            entry.delete(0, "end")
            entry.insert(0, value)

        self.add_button.configure(state="disabled")
        self.update_button.configure(state="normal")
        self.delete_button.configure(state="normal")

        self.update_status(
            f"Employee selected: {values[1]} {values[2]}"
        )

    def handle_table_double_click(self, event=None):
        self.handle_table_selection()
        self.first_name_entry.focus_set()

    # ---------------------------------------------------------
    # FORM UTILITIES
    # ---------------------------------------------------------

    def clear_form(self):
        self.selected_employee_id = None

        for entry in (
            self.first_name_entry,
            self.last_name_entry,
            self.position_entry,
            self.hire_date_entry,
            self.phone_number_entry,
        ):
            entry.delete(0, "end")

        for item in self.employee_table.selection():
            self.employee_table.selection_remove(item)

        self.add_button.configure(state="normal")
        self.update_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")

        self.first_name_entry.focus_set()
        self.update_status("Employee form cleared.")

    # ---------------------------------------------------------
    # CALLBACKS TO MAIN APPLICATION
    # ---------------------------------------------------------

    def update_status(self, message):
        if callable(self.status_callback):
            self.status_callback(message)

    def refresh_dashboard(self):
        if callable(self.dashboard_callback):
            self.dashboard_callback()
