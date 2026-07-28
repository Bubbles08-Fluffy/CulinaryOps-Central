import customtkinter as ctk

from database.vendors import count_vendors
from database.employees import count_employees
from database.invoices import (
    count_invoices,
    count_pending_invoices,
)

from gui.vendors import VendorsPage
from gui.employees import EmployeesPage
from gui.invoices import InvoicesPage
from gui.meals import MealsPage
from gui.sales import SalesPage
from database.sales import get_total_sales

from gui.theme import (
    TITLE_FONT,
    HEADER_FONT,
    TEXT_FONT,
    BUTTON_FONT,
    CARD_TITLE_FONT,
    CARD_VALUE_FONT,
)


class CulinaryOpsApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("CulinaryOps Central")
        self.geometry("1450x850")
        self.minsize(1300, 800)

        self.active_button = None
        self.navigation_buttons = {}

        self.create_layout()
        self.refresh_dashboard_cards()
        self.show_dashboard_page()

    # =========================================================
    # MAIN APPLICATION LAYOUT
    # =========================================================

    def create_layout(self):

        self.main_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.main_container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.create_header()
        self.create_dashboard_cards()
        self.create_content_area()
        self.create_status_bar()

    # =========================================================
    # HEADER
    # =========================================================

    def create_header(self):

        self.header_frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=12,
            height=100
        )
        self.header_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        self.header_frame.pack_propagate(False)

        left_header = ctk.CTkFrame(
            self.header_frame,
            fg_color="transparent"
        )
        left_header.pack(
            side="left",
            padx=20,
            pady=15
        )

        ctk.CTkLabel(
            left_header,
            text="CulinaryOps Central",
            font=TITLE_FONT
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_header,
            text="Dining Services Management System",
            font=TEXT_FONT,
            text_color=("gray35", "gray75")
        ).pack(anchor="w", pady=(2, 0))

        right_header = ctk.CTkFrame(
            self.header_frame,
            fg_color="transparent"
        )
        right_header.pack(
            side="right",
            padx=20,
            pady=15
        )

        ctk.CTkLabel(
            right_header,
            text="Administrator",
            font=HEADER_FONT
        ).pack(anchor="e")

        ctk.CTkLabel(
            right_header,
            text="Version 1.0",
            font=TEXT_FONT,
            text_color=("gray35", "gray75")
        ).pack(anchor="e", pady=(2, 0))

    # =========================================================
    # DASHBOARD CARDS
    # =========================================================

    def create_dashboard_cards(self):

        self.dashboard_frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=12,
            height=120
        )
        self.dashboard_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        self.dashboard_frame.pack_propagate(False)

        for column in range(5):
            self.dashboard_frame.grid_columnconfigure(
                column,
                weight=1,
                uniform="dashboard_cards"
            )

        self.vendor_card_value = self.create_card(
            title="Vendors",
            value="0",
            column=0
        )

        self.employee_card_value = self.create_card(
            title="Employees",
            value="0",
            column=1
        )

        self.invoice_card_value = self.create_card(
            title="Invoices",
            value="0",
            column=2
        )

        self.pending_invoice_card_value = self.create_card(
            title="Pending Invoices",
            value="0",
            column=3
        )

        self.sales_card_value = self.create_card(
            title="Total Sales",
            value="$0.00",
            column=4
        )

    def create_card(self, title, value, column):

        card = ctk.CTkFrame(
            self.dashboard_frame,
            corner_radius=10,
            border_width=1,
            border_color=("gray70", "gray30")
        )
        card.grid(
            row=0,
            column=column,
            padx=8,
            pady=12,
            sticky="nsew"
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=CARD_TITLE_FONT,
            text_color=("gray35", "gray75")
        ).pack(pady=(14, 2))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=CARD_VALUE_FONT
        )
        value_label.pack(pady=(0, 12))

        return value_label

    # =========================================================
    # SIDEBAR AND WORKSPACE
    # =========================================================

    def create_content_area(self):

        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        self.content_frame.pack(
            fill="both",
            expand=True
        )

        self.create_sidebar()
        self.create_workspace()

    def create_sidebar(self):

        self.sidebar_frame = ctk.CTkFrame(
            self.content_frame,
            width=220,
            corner_radius=12
        )
        self.sidebar_frame.pack(
            side="left",
            fill="y",
            padx=(0, 10)
        )

        self.sidebar_frame.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar_frame,
            text="Navigation",
            font=HEADER_FONT
        ).pack(pady=(22, 20))

        navigation_items = [
            ("Dashboard", self.show_dashboard_page),
            ("Vendors", self.show_vendors_page),
            ("Invoices", self.show_invoices_page),
            ("Employees", self.show_employees_page),
            ("Meal Counts", self.show_meals_page),
            ("Sales", self.show_sales_page),
            ("Reports", self.show_reports_page),
        ]

        for button_name, command in navigation_items:

            button = ctk.CTkButton(
                self.sidebar_frame,
                text=button_name,
                width=180,
                height=42,
                corner_radius=8,
                font=BUTTON_FONT,
                anchor="w",
                command=command
            )
            button.pack(pady=6)

            self.navigation_buttons[button_name] = button

        ctk.CTkLabel(
            self.sidebar_frame,
            text="CulinaryOps Central\nDatabase Management",
            justify="center",
            font=("Segoe UI", 11),
            text_color=("gray45", "gray65")
        ).pack(side="bottom", pady=20)

    def create_workspace(self):

        self.workspace_frame = ctk.CTkFrame(
            self.content_frame,
            corner_radius=12
        )
        self.workspace_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

    # =========================================================
    # STATUS BAR
    # =========================================================

    def create_status_bar(self):

        self.status_frame = ctk.CTkFrame(
            self.main_container,
            height=38,
            corner_radius=10
        )
        self.status_frame.pack(
            fill="x",
            pady=(10, 0)
        )

        self.status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status: Ready",
            font=("Segoe UI", 12)
        )
        self.status_label.pack(
            side="left",
            padx=15,
            pady=7
        )

    def update_status(self, message):

        self.status_label.configure(
            text=f"Status: {message}"
        )

    def refresh_dashboard_cards(self):
        """Refresh dashboard values connected to SQLite."""

        #Vendor Count
        try:
            self.vendor_card_value.configure(
                text=str(count_vendors())
            )
        except Exception:
            self.vendor_card_value.configure(
                text="--"
            )

        #Employee Count
        try:
            self.employee_card_value.configure(
                text=str(count_employees())
            )
        except Exception:
            self.employee_card_value.configure(
                text="--"
            )

        #Invoice Count
        try:
            self.invoice_card_value.configure(
                text=str(count_invoices())
            )
        except Exception:
            self.invoice_card_value.configure(
                text="--"
            )

        #Pending Invoice Count
        try:
            self.pending_invoice_card_value.configure(
                text=str(count_pending_invoices())
            )
        except Exception:
            self.pending_invoice_card_value.configure(
                text="--"
            )

        #Total Sales Revenue
        try:
            total_sales = get_total_sales()
            self.sales_card_value.configure(
                    text=f"${total_sales:,.2f}"
                )
        except Exception:
            self.sales_card_value.configure(
                text="$0.00"
            )

    # =========================================================
    # PAGE MANAGEMENT
    # =========================================================

    def clear_workspace(self):

        for widget in self.workspace_frame.winfo_children():
            widget.destroy()

    def set_active_button(self, button_name):

        if self.active_button is not None:
            self.active_button.configure(
                fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]
            )

        selected_button = self.navigation_buttons.get(button_name)

        if selected_button is not None:
            selected_button.configure(
                fg_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"]
            )
            self.active_button = selected_button

    def create_page_header(self, title, description):

        ctk.CTkLabel(
            self.workspace_frame,
            text=title,
            font=TITLE_FONT
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 5)
        )

        ctk.CTkLabel(
            self.workspace_frame,
            text=description,
            font=TEXT_FONT,
            text_color=("gray35", "gray70")
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

    def create_placeholder_panel(self, message):

        panel = ctk.CTkFrame(
            self.workspace_frame,
            corner_radius=10,
            border_width=1,
            border_color=("gray70", "gray30")
        )
        panel.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 25)
        )

        ctk.CTkLabel(
            panel,
            text=message,
            font=TEXT_FONT,
            justify="center"
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

    # =========================================================
    # DASHBOARD PAGE
    # =========================================================

    def show_dashboard_page(self):

        self.clear_workspace()
        self.set_active_button("Dashboard")

        self.create_page_header(
            "Dashboard",
            "Overview of dining services operations and database activity."
        )

        welcome_panel = ctk.CTkFrame(
            self.workspace_frame,
            corner_radius=10,
            border_width=1,
            border_color=("gray70", "gray30")
        )
        welcome_panel.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 25)
        )

        ctk.CTkLabel(
            welcome_panel,
            text="Welcome to CulinaryOps Central",
            font=HEADER_FONT
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 8)
        )

        welcome_text = (
            "Use the navigation menu to manage the dining services database.\n\n"
            "Available management areas:\n\n"
            "• Vendors and vendor contact information\n"
            "• Invoices and payment status\n"
            "• Employee records\n"
            "• Daily meal counts\n"
            "• Sales records\n"
            "• Operational reports and CSV exports\n\n"
            "The summary cards above will display live database totals "
            "once the database functions are connected."
        )

        ctk.CTkLabel(
            welcome_panel,
            text=welcome_text,
            font=TEXT_FONT,
            justify="left"
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 25)
        )

        self.update_status("Dashboard loaded")

    # =========================================================
    # PLACEHOLDER PAGES
    # =========================================================

    def show_vendors_page(self):

        self.clear_workspace()
        self.set_active_button("Vendors")

        vendors_page = VendorsPage(
            self.workspace_frame,
            status_callback=self.update_status,
            dashboard_callback=self.refresh_dashboard_cards,
        )
        vendors_page.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15,
        )

        self.update_status("Vendor Management opened")

    def show_invoices_page(self):

        self.clear_workspace()
        self.set_active_button("Invoices")

        invoices_page = InvoicesPage(
            self.workspace_frame,
            status_callback=self.update_status,
            dashboard_callback=self.refresh_dashboard_cards,
        )

        invoices_page.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15,
        )

        self.update_status("Invoice Management opened")

    def show_employees_page(self):

        self.clear_workspace()
        self.set_active_button("Employees")

        employees_page = EmployeesPage(
            self.workspace_frame,
            status_callback=self.update_status,
            dashboard_callback=self.refresh_dashboard_cards,
        )

        employees_page.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15,
        )

        self.update_status("Employee Management opened")

    def show_meals_page(self):

        self.clear_workspace()
        self.set_active_button("Meal Counts")

        meals_page = MealsPage(
            self.workspace_frame,
            status_callback=self.update_status,
            dashboard_callback=self.refresh_dashboard_cards,
        )

        meals_page.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15,
        )

        self.update_status("Meal Count Management opened")

    def show_sales_page(self):

        self.clear_workspace()
        self.set_active_button("Sales")

        sales_page = SalesPage(
            self.workspace_frame,
            status_callback=self.update_status,
            dashboard_callback=self.refresh_dashboard_cards,
        )

        sales_page.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15,
        )

        self.update_status("Sales Records opened")

    def show_reports_page(self):

        self.clear_workspace()
        self.set_active_button("Reports")

        self.create_page_header(
        "Reports",
        "Generate operational summaries and export report data."
    )

        self.create_placeholder_panel(
        "Reports module planned for the next version.\n\n"
        "Current application provides live operational summaries "
        "through the Dashboard."
    )

        self.update_status("Reports opened")