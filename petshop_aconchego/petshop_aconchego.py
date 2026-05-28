import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, W, X, Button, Entry, Frame, Label, LabelFrame, Listbox, StringVar, Text, Tk, Toplevel, messagebox, ttk


APP_TITLE = "Pet Shop Aconchego"
DATA_FILE = Path(__file__).with_name("petshop_aconchego_dados.json")
BUFFER_MINUTES = 15
WORK_DAY_START = "08:00"
WORK_DAY_END = "18:00"

BREEDS = {
    "Yorkshire": ("P", 4),
    "Shih Tzu": ("P", 6),
    "Poodle": ("M", 14),
    "Border Collie": ("M", 18),
    "Golden Retriever": ("G", 30),
    "Labrador": ("G", 32),
    "Outra": ("M", 12),
}

SERVICE_MATRIX = {
    "Banho": {"P": 40, "M": 60, "G": 90},
    "Tosa": {"P": 30, "M": 45, "G": 60},
    "Banho + Tosa": {"P": 60, "M": 90, "G": 120},
}

SERVICE_PRICES = {
    "Banho": {"P": 55.0, "M": 75.0, "G": 100.0},
    "Tosa": {"P": 45.0, "M": 60.0, "G": 85.0},
    "Banho + Tosa": {"P": 90.0, "M": 120.0, "G": 160.0},
}

SERVICE_INPUTS = {
    "Banho": {"Shampoo": 50, "Condicionador": 30, "Toalha descartavel": 1},
    "Tosa": {"Lamina": 1},
    "Banho + Tosa": {"Shampoo": 50, "Condicionador": 30, "Toalha descartavel": 1, "Lamina": 1},
}

MANAGEMENT_TEAM = {
    "Gerente": "Gestao de custos, ticket medio e auditoria de estoque",
    "Administrador": "Faturamento, conciliacao bancaria e gestao de agenda",
}

BATH_GROOMING_EMPLOYEES = {
    "Joao": ["Banho", "Banho + Tosa"],
    "Maria": ["Banho", "Tosa", "Banho + Tosa"],
    "Carlos": ["Tosa", "Banho + Tosa"],
    "Bruno": ["Banho", "Tosa"],
}

DAYCARE_CAREGIVERS = ["Ana", "Fernanda", "Lucas", "Beatriz"]

DAYCARE_PLANS = {
    "Diaria avulsa": {"P": 50.0, "M": 60.0, "G": 75.0},
    "Pacote 2x semana": {"P": 300.0, "M": 350.0, "G": 430.0},
    "Pacote 3x semana": {"P": 420.0, "M": 480.0, "G": 580.0},
    "Mensal livre": {"P": 600.0, "M": 700.0, "G": 850.0},
}

EMPLOYEES = BATH_GROOMING_EMPLOYEES

INTERCURRENCES = ["Agressividade", "Parasitas", "Lesao Previa", "Anormalidade na Pele"]

ACCESS = {
    "Gerente": {"agenda", "estoque", "operacional", "creche", "dashboard"},
    "Administrativo": {"agenda", "creche", "dashboard"},
    "Operacional": {"operacional", "creche"},
}


def next_business_start():
    now = datetime.now().replace(second=0, microsecond=0)
    work_start = datetime.strptime(WORK_DAY_START, "%H:%M").time()
    work_end = datetime.strptime(WORK_DAY_END, "%H:%M").time()

    if now.time() < work_start:
        return now.replace(hour=work_start.hour, minute=work_start.minute)

    if now.time() >= work_end:
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=work_start.hour, minute=work_start.minute)

    minute = 30 if now.minute < 30 else 0
    hour = now.hour if now.minute < 30 else now.hour + 1
    candidate = now.replace(hour=hour, minute=minute)

    if candidate.time() >= work_end:
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=work_start.hour, minute=work_start.minute)

    return candidate


@dataclass
class Product:
    name: str
    unit: str
    stock: float
    critical_level: float
    estimated_usage: float = 0.0


@dataclass
class Appointment:
    id: int
    tutor: str
    pet: str
    breed: str
    service: str
    date: str
    start_time: str
    duration: int
    buffer: int
    price: float
    employee: str = "Nao definido"
    payment_status: str = "Pendente"
    service_status: str = "Agendado"
    intercorrences: list[str] = None

    def __post_init__(self):
        if self.intercorrences is None:
            self.intercorrences = []


@dataclass
class DaycareStay:
    id: int
    tutor: str
    pet: str
    breed: str
    date: str
    start_time: str
    end_time: str
    caregiver: str
    plan: str = "Diaria avulsa"
    price: float = 60.0
    notes: str = ""
    status: str = "Na creche"


class Store:
    def __init__(self):
        self.products: list[Product] = []
        self.appointments: list[Appointment] = []
        self.daycare_stays: list[DaycareStay] = []
        self.stock_break_risks = 0
        self.load()

    def load(self):
        if not DATA_FILE.exists():
            self.products = [
                Product("Shampoo", "ml", 1000, 200),
                Product("Condicionador", "ml", 800, 150),
                Product("Toalha descartavel", "un", 50, 10),
                Product("Lamina", "un", 20, 5),
            ]
            self.appointments = []
            self.daycare_stays = []
            self.save()
            return

        with DATA_FILE.open("r", encoding="utf-8") as file:
            raw = json.load(file)

        self.products = [Product(**item) for item in raw.get("products", [])]
        self.appointments = [Appointment(**item) for item in raw.get("appointments", [])]
        self.daycare_stays = []
        for item in raw.get("daycare_stays", []):
            item.setdefault("breed", "Outra")
            self.daycare_stays.append(DaycareStay(**item))
        self.stock_break_risks = raw.get("stock_break_risks", 0)

    def save(self):
        payload = {
            "products": [asdict(product) for product in self.products],
            "appointments": [asdict(appointment) for appointment in self.appointments],
            "daycare_stays": [asdict(stay) for stay in self.daycare_stays],
            "stock_break_risks": self.stock_break_risks,
        }
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)

    def next_appointment_id(self):
        return max([appointment.id for appointment in self.appointments], default=0) + 1

    def next_daycare_id(self):
        return max([stay.id for stay in self.daycare_stays], default=0) + 1

    def product_by_name(self, name):
        return next((product for product in self.products if product.name == name), None)

    def has_pending_payment_for_pet(self, pet):
        return any(
            appointment.pet.lower() == pet.lower()
            and appointment.payment_status != "Confirmado"
            and appointment.service_status != "Cancelado"
            for appointment in self.appointments
        )

    def appointment_times(self, appointment):
        start = datetime.strptime(f"{appointment.date} {appointment.start_time}", "%d/%m/%Y %H:%M")
        end = start + timedelta(minutes=appointment.duration + appointment.buffer)
        return start, end

    def time_conflict(self, date, start_time, duration, employee, ignore_id=None):
        new_start = datetime.strptime(f"{date} {start_time}", "%d/%m/%Y %H:%M")
        new_end = new_start + timedelta(minutes=duration + BUFFER_MINUTES)

        day_start = datetime.strptime(f"{date} {WORK_DAY_START}", "%d/%m/%Y %H:%M")
        day_end = datetime.strptime(f"{date} {WORK_DAY_END}", "%d/%m/%Y %H:%M")
        if new_start < day_start or new_end > day_end:
            return "Fora do horario comercial (08:00 as 18:00)."

        for appointment in self.appointments:
            if (
                appointment.id == ignore_id
                or appointment.date != date
                or appointment.employee != employee
                or appointment.service_status == "Cancelado"
            ):
                continue
            current_start, current_end = self.appointment_times(appointment)
            if new_start < current_end and new_end > current_start:
                return f"{employee} ja esta ocupado com {appointment.pet} as {appointment.start_time}."
        return None

    def available_employees(self, service, date, start_time, duration):
        available = []
        for employee, services in EMPLOYEES.items():
            if service in services and self.time_conflict(date, start_time, duration, employee) is None:
                available.append(employee)
        return available

    def check_stock_for_service(self, service, count_risk=False):
        missing = []
        critical_after_service = False
        for product_name, quantity in SERVICE_INPUTS[service].items():
            product = self.product_by_name(product_name)
            if product is None or product.stock < quantity:
                missing.append(product_name)
            elif product.stock - quantity <= product.critical_level:
                critical_after_service = True
        if critical_after_service and count_risk:
            self.stock_break_risks += 1
        return missing

    def consume_inputs(self, service):
        used_items = []
        for product_name, quantity in SERVICE_INPUTS[service].items():
            product = self.product_by_name(product_name)
            if product:
                product.stock -= quantity
                product.estimated_usage += quantity
                used_items.append(f"{product_name}: {quantity} {product.unit}")
        return used_items


class PetShopApp:
    def __init__(self, root):
        self.root = root
        self.store = Store()
        self.current_profile = StringVar(value="Gerente")
        self.selected_appointment_id = None
        self.countdown_seconds = 0
        self.timer_running = False
        self.appointment_timers = {}
        self.running_timers = set()

        root.title(APP_TITLE)
        root.geometry("1120x720")
        root.minsize(960, 620)

        self.build_layout()
        self.refresh_all()

    def build_layout(self):
        top = Frame(self.root, padx=14, pady=10)
        top.pack(fill=X)

        Label(top, text=APP_TITLE, font=("Arial", 18, "bold")).pack(side=LEFT)
        Label(top, text="Perfil:").pack(side=LEFT, padx=(30, 6))
        profile_box = ttk.Combobox(top, textvariable=self.current_profile, values=list(ACCESS), state="readonly", width=18)
        profile_box.pack(side=LEFT)
        profile_box.bind("<<ComboboxSelected>>", lambda _event: self.apply_access())

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill=BOTH, expand=True, padx=14, pady=(0, 14))

        self.agenda_tab = Frame(self.tabs, padx=12, pady=12)
        self.stock_tab = Frame(self.tabs, padx=12, pady=12)
        self.operation_tab = Frame(self.tabs, padx=12, pady=12)
        self.daycare_tab = Frame(self.tabs, padx=12, pady=12)
        self.dashboard_tab = Frame(self.tabs, padx=12, pady=12)

        self.tabs.add(self.agenda_tab, text="Agenda")
        self.tabs.add(self.stock_tab, text="Estoque")
        self.tabs.add(self.operation_tab, text="Operacional")
        self.tabs.add(self.daycare_tab, text="Creche")
        self.tabs.add(self.dashboard_tab, text="Dashboard")

        self.build_agenda_tab()
        self.build_stock_tab()
        self.build_operation_tab()
        self.build_daycare_tab()
        self.build_dashboard_tab()

    def build_agenda_tab(self):
        form = LabelFrame(self.agenda_tab, text="Novo agendamento", padx=10, pady=10)
        form.pack(side=LEFT, fill=BOTH, padx=(0, 10))

        self.tutor_var = StringVar()
        self.pet_var = StringVar()
        self.breed_var = StringVar(value=list(BREEDS)[0])
        self.service_var = StringVar(value=list(SERVICE_MATRIX)[0])
        self.employee_var = StringVar(value=list(EMPLOYEES)[0])
        initial_datetime = next_business_start()
        self.date_var = StringVar(value=initial_datetime.strftime("%d/%m/%Y"))
        self.time_var = StringVar(value=initial_datetime.strftime("%H:%M"))
        self.preview_var = StringVar()

        self.add_labeled_entry(form, "Tutor", self.tutor_var)
        self.add_labeled_entry(form, "Pet", self.pet_var)
        self.add_combo(form, "Raca", self.breed_var, list(BREEDS))
        self.add_combo(form, "Servico", self.service_var, list(SERVICE_MATRIX))
        self.add_combo(form, "Funcionario banho/tosa", self.employee_var, list(EMPLOYEES))
        self.add_labeled_entry(form, "Data (dd/mm/aaaa)", self.date_var)
        self.add_labeled_entry(form, "Hora (hh:mm)", self.time_var)

        Label(form, textvariable=self.preview_var, justify=LEFT, fg="#1f5f8b").pack(anchor=W, pady=8)
        Button(form, text="Agendar", command=self.create_appointment).pack(fill=X, pady=4)

        list_frame = LabelFrame(self.agenda_tab, text="Agenda por funcionario", padx=10, pady=10)
        list_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.appointment_tree = ttk.Treeview(
            list_frame,
            columns=("id", "date", "time", "employee", "pet", "service", "duration", "payment", "status"),
            show="headings",
        )
        headers = {
            "id": "ID",
            "date": "Data",
            "time": "Hora",
            "employee": "Funcionario",
            "pet": "Pet",
            "service": "Servico",
            "duration": "Tempo + Buffer",
            "payment": "Pagamento",
            "status": "Status",
        }
        for column, title in headers.items():
            self.appointment_tree.heading(column, text=title)
            self.appointment_tree.column(column, width=105)
        self.appointment_tree.pack(fill=BOTH, expand=True)

        action_bar = Frame(list_frame, pady=8)
        action_bar.pack(fill=X)
        Button(action_bar, text="Pagamento confirmado", command=self.confirm_payment).pack(side=LEFT, padx=4)
        Button(action_bar, text="Cancelar", command=self.cancel_appointment).pack(side=LEFT, padx=4)
        Button(action_bar, text="Excluir", command=self.delete_appointment).pack(side=LEFT, padx=4)

    def build_stock_tab(self):
        left = LabelFrame(self.stock_tab, text="Produtos", padx=10, pady=10)
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        self.stock_tree = ttk.Treeview(left, columns=("name", "unit", "stock", "critical", "usage"), show="headings")
        for column, title in {
            "name": "Produto",
            "unit": "Unidade",
            "stock": "Estoque",
            "critical": "Nivel critico",
            "usage": "Uso estimado",
        }.items():
            self.stock_tree.heading(column, text=title)
            self.stock_tree.column(column, width=120)
        self.stock_tree.pack(fill=BOTH, expand=True)

        form = LabelFrame(self.stock_tab, text="Cadastrar / repor", padx=10, pady=10)
        form.pack(side=RIGHT, fill=BOTH)
        self.product_name_var = StringVar()
        self.product_unit_var = StringVar(value="ml")
        self.product_stock_var = StringVar()
        self.product_critical_var = StringVar()

        self.add_labeled_entry(form, "Produto", self.product_name_var)
        self.add_labeled_entry(form, "Unidade", self.product_unit_var)
        self.add_labeled_entry(form, "Quantidade", self.product_stock_var)
        self.add_labeled_entry(form, "Nivel critico", self.product_critical_var)
        Button(form, text="Salvar produto", command=self.save_product).pack(fill=X, pady=4)
        Button(form, text="Relatorio de desperdicio", command=self.show_waste_report).pack(fill=X, pady=4)

    def build_operation_tab(self):
        left = LabelFrame(self.operation_tab, text="Servicos aguardando execucao", padx=10, pady=10)
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        self.operation_list = Listbox(left)
        self.operation_list.pack(fill=BOTH, expand=True)
        self.operation_list.bind("<<ListboxSelect>>", lambda _event: self.select_operation())

        right = LabelFrame(self.operation_tab, text="Execucao", padx=10, pady=10)
        right.pack(side=RIGHT, fill=BOTH)
        self.operation_selected_var = StringVar(value="Nenhum servico selecionado")
        self.timer_var = StringVar(value="00:00")
        self.used_items_var = StringVar(value="Itens utilizados aparecerao aqui apos finalizar.")
        Label(right, textvariable=self.operation_selected_var, wraplength=260, justify=LEFT).pack(anchor=W, pady=4)
        Label(right, textvariable=self.timer_var, font=("Arial", 28, "bold"), fg="#2c3e50").pack(pady=14)
        Button(right, text="Iniciar cronometro", command=self.start_timer).pack(fill=X, pady=4)
        Button(right, text="Pausar cronometro", command=self.pause_timer).pack(fill=X, pady=4)
        Button(right, text="Finalizar servico", command=self.finish_service).pack(fill=X, pady=4)
        Label(right, textvariable=self.used_items_var, wraplength=260, justify=LEFT, fg="#1f5f8b").pack(anchor=W, pady=(10, 4))

        Label(right, text="Intercorrencias").pack(anchor=W, pady=(16, 4))
        self.intercurrence_vars = {name: StringVar(value="0") for name in INTERCURRENCES}
        for name, variable in self.intercurrence_vars.items():
            ttk.Checkbutton(right, text=name, variable=variable, onvalue="1", offvalue="0").pack(anchor=W)

    def build_daycare_tab(self):
        form = LabelFrame(self.daycare_tab, text="Entrada na creche", padx=10, pady=10)
        form.pack(side=LEFT, fill=BOTH, padx=(0, 10))

        initial_datetime = next_business_start()
        self.daycare_tutor_var = StringVar()
        self.daycare_pet_var = StringVar()
        self.daycare_breed_var = StringVar(value=list(BREEDS)[0])
        self.daycare_date_var = StringVar(value=initial_datetime.strftime("%d/%m/%Y"))
        self.daycare_start_var = StringVar(value=initial_datetime.strftime("%H:%M"))
        self.daycare_end_var = StringVar(value="18:00")
        self.daycare_caregiver_var = StringVar(value=DAYCARE_CAREGIVERS[0])
        self.daycare_plan_var = StringVar(value=list(DAYCARE_PLANS)[0])
        self.daycare_price_var = StringVar()
        self.daycare_notes_var = StringVar()

        self.add_labeled_entry(form, "Tutor", self.daycare_tutor_var)
        self.add_labeled_entry(form, "Pet", self.daycare_pet_var)
        self.add_combo(form, "Raca", self.daycare_breed_var, list(BREEDS))
        self.add_labeled_entry(form, "Data (dd/mm/aaaa)", self.daycare_date_var)
        self.add_labeled_entry(form, "Entrada (hh:mm)", self.daycare_start_var)
        self.add_labeled_entry(form, "Saida prevista (hh:mm)", self.daycare_end_var)
        self.add_combo(form, "Cuidador", self.daycare_caregiver_var, DAYCARE_CAREGIVERS)
        self.add_combo(form, "Plano", self.daycare_plan_var, list(DAYCARE_PLANS))
        Label(form, textvariable=self.daycare_price_var, fg="#1f5f8b").pack(anchor=W, pady=(4, 0))
        self.add_labeled_entry(form, "Observacoes", self.daycare_notes_var)
        self.update_daycare_price()
        Button(form, text="Registrar entrada", command=self.create_daycare_stay).pack(fill=X, pady=4)
        Button(form, text="Registrar saida", command=self.finish_daycare_stay).pack(fill=X, pady=4)

        list_frame = LabelFrame(self.daycare_tab, text="Pets na creche", padx=10, pady=10)
        list_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.daycare_tree = ttk.Treeview(
            list_frame,
            columns=("id", "date", "start", "end", "caregiver", "pet", "breed", "tutor", "plan", "price", "status"),
            show="headings",
        )
        headers = {
            "id": "ID",
            "date": "Data",
            "start": "Entrada",
            "end": "Saida prev.",
            "caregiver": "Cuidador",
            "pet": "Pet",
            "breed": "Raca",
            "tutor": "Tutor",
            "plan": "Plano",
            "price": "Valor",
            "status": "Status",
        }
        for column, title in headers.items():
            self.daycare_tree.heading(column, text=title)
            self.daycare_tree.column(column, width=105)
        self.daycare_tree.pack(fill=BOTH, expand=True)

    def build_dashboard_tab(self):
        self.dashboard_text = Text(self.dashboard_tab, font=("Consolas", 11), wrap="word", height=28)
        dashboard_scroll = ttk.Scrollbar(self.dashboard_tab, orient="vertical", command=self.dashboard_text.yview)
        self.dashboard_text.configure(yscrollcommand=dashboard_scroll.set)
        self.dashboard_text.pack(side=LEFT, fill=BOTH, expand=True)
        dashboard_scroll.pack(side=RIGHT, fill="y")

    def add_labeled_entry(self, parent, label, variable):
        Label(parent, text=label).pack(anchor=W, pady=(5, 0))
        Entry(parent, textvariable=variable, width=30).pack(fill=X)

    def add_combo(self, parent, label, variable, values):
        Label(parent, text=label).pack(anchor=W, pady=(5, 0))
        combo = ttk.Combobox(parent, textvariable=variable, values=values, state="readonly", height=10)
        combo.pack(fill=X)
        combo.bind("<<ComboboxSelected>>", lambda _event: self.update_preview())
        if variable is getattr(self, "daycare_plan_var", None) or variable is getattr(self, "daycare_breed_var", None):
            combo.bind("<<ComboboxSelected>>", lambda _event: self.update_daycare_price())

    def apply_access(self):
        allowed = ACCESS[self.current_profile.get()]
        tabs = {
            "agenda": self.agenda_tab,
            "estoque": self.stock_tab,
            "operacional": self.operation_tab,
            "creche": self.daycare_tab,
            "dashboard": self.dashboard_tab,
        }
        for key, tab in tabs.items():
            try:
                self.tabs.tab(tab, state="normal" if key in allowed else "disabled")
            except Exception:
                pass
        self.refresh_all()

    def selected_tree_id(self):
        selected = self.appointment_tree.selection()
        if not selected:
            messagebox.showwarning("Selecao obrigatoria", "Selecione um agendamento.")
            return None
        return int(self.appointment_tree.item(selected[0])["values"][0])

    def selected_daycare_id(self):
        selected = self.daycare_tree.selection()
        if not selected:
            messagebox.showwarning("Selecao obrigatoria", "Selecione um pet na creche.")
            return None
        return int(self.daycare_tree.item(selected[0])["values"][0])

    def find_appointment(self, appointment_id):
        return next((appointment for appointment in self.store.appointments if appointment.id == appointment_id), None)

    def find_daycare_stay(self, stay_id):
        return next((stay for stay in self.store.daycare_stays if stay.id == stay_id), None)

    def service_data(self):
        breed = self.breed_var.get()
        service = self.service_var.get()
        size, weight = BREEDS[breed]
        duration = SERVICE_MATRIX[service][size]
        price = SERVICE_PRICES[service][size]
        return size, weight, duration, price

    def update_preview(self):
        size, weight, duration, price = self.service_data()
        total = duration + BUFFER_MINUTES
        employee = self.employee_var.get()
        employee_services = ", ".join(EMPLOYEES.get(employee, []))
        self.preview_var.set(
            f"Porte: {size} | Peso medio: {weight}kg\n"
            f"Tempo bloqueado: {duration} min + {BUFFER_MINUTES} min limpeza = {total} min\n"
            f"Valor previsto: R$ {price:.2f}\n"
            f"{employee} atende: {employee_services}"
        )

    def update_daycare_price(self):
        breed = self.daycare_breed_var.get()
        size, weight = BREEDS[breed]
        price = DAYCARE_PLANS.get(self.daycare_plan_var.get(), {}).get(size, 0.0)
        self.daycare_price_var.set(f"Porte: {size} | Peso medio: {weight}kg | Valor do plano: R$ {price:.2f}")

    def create_appointment(self):
        try:
            appointment_date = datetime.strptime(f"{self.date_var.get()} {self.time_var.get()}", "%d/%m/%Y %H:%M")
        except ValueError:
            messagebox.showerror("Data invalida", "Use data dd/mm/aaaa e hora hh:mm.")
            return

        if appointment_date < datetime.now():
            messagebox.showerror("Data invalida", "Nao e permitido agendar antes da data/hora atual.")
            return

        if not self.tutor_var.get().strip() or not self.pet_var.get().strip():
            messagebox.showerror("Campos obrigatorios", "Informe tutor e pet.")
            return

        if self.store.has_pending_payment_for_pet(self.pet_var.get()):
            messagebox.showerror("Trava financeira", "Este pet possui pagamento pendente. Confirme antes de novo agendamento.")
            return

        _size, _weight, duration, price = self.service_data()
        service = self.service_var.get()
        employee = self.employee_var.get()

        if service not in EMPLOYEES.get(employee, []):
            messagebox.showerror("Funcionario indisponivel", f"{employee} nao executa o servico {service}.")
            return

        conflict = self.store.time_conflict(self.date_var.get(), self.time_var.get(), duration, employee)
        if conflict:
            available = self.store.available_employees(service, self.date_var.get(), self.time_var.get(), duration)
            suggestion = f"\nDisponivel no horario: {', '.join(available)}" if available else "\nNenhum funcionario livre para esse servico."
            messagebox.showerror("Choque de horario", conflict + suggestion)
            return

        missing = self.store.check_stock_for_service(service)
        if missing:
            messagebox.showerror("Estoque insuficiente", "Insumos indisponiveis: " + ", ".join(missing))
            return

        appointment = Appointment(
            id=self.store.next_appointment_id(),
            tutor=self.tutor_var.get().strip(),
            pet=self.pet_var.get().strip(),
            breed=self.breed_var.get(),
            service=service,
            date=self.date_var.get(),
            start_time=self.time_var.get(),
            duration=duration,
            buffer=BUFFER_MINUTES,
            price=price,
            employee=employee,
        )
        self.store.appointments.append(appointment)
        self.store.save()
        self.refresh_all()
        messagebox.showinfo("Agendamento criado", "Horario bloqueado com buffer sanitario obrigatorio.")

    def confirm_payment(self):
        appointment_id = self.selected_tree_id()
        if appointment_id is None:
            return
        appointment = self.find_appointment(appointment_id)
        appointment.payment_status = "Confirmado"
        self.store.save()
        self.refresh_all()

    def cancel_appointment(self):
        appointment_id = self.selected_tree_id()
        if appointment_id is None:
            return
        appointment = self.find_appointment(appointment_id)
        appointment.service_status = "Cancelado"
        self.store.save()
        self.refresh_all()

    def delete_appointment(self):
        appointment_id = self.selected_tree_id()
        if appointment_id is None:
            return

        appointment = self.find_appointment(appointment_id)
        if appointment is None:
            return

        confirm = messagebox.askyesno(
            "Confirmar exclusao",
            f"Deseja realmente excluir o atendimento de {appointment.pet}?"
        )
        if not confirm:
            return

        self.store.appointments = [
            item for item in self.store.appointments
            if item.id != appointment_id
        ]
        self.appointment_timers.pop(appointment_id, None)
        self.running_timers.discard(appointment_id)
        if self.selected_appointment_id == appointment_id:
            self.selected_appointment_id = None
            self.countdown_seconds = 0
            self.update_timer_label()

        self.store.save()
        self.refresh_all()
        messagebox.showinfo("Excluido", "Atendimento removido com sucesso.")

    def save_product(self):
        try:
            quantity = float(self.product_stock_var.get().replace(",", "."))
            critical = float(self.product_critical_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Numero invalido", "Quantidade e nivel critico devem ser numeros.")
            return

        name = self.product_name_var.get().strip()
        unit = self.product_unit_var.get().strip()
        if not name or not unit:
            messagebox.showerror("Campos obrigatorios", "Informe produto e unidade.")
            return

        product = self.store.product_by_name(name)
        if product:
            product.unit = unit
            product.stock += quantity
            product.critical_level = critical
        else:
            self.store.products.append(Product(name, unit, quantity, critical))
        self.store.save()
        self.refresh_all()

    def show_waste_report(self):
        window = Toplevel(self.root)
        window.title("Relatorio de desperdicio")
        window.geometry("520x320")
        text = Listbox(window)
        text.pack(fill=BOTH, expand=True, padx=12, pady=12)
        for product in self.store.products:
            physical = product.stock
            estimated = product.estimated_usage
            text.insert(END, f"{product.name}: uso estimado {estimated:.1f} {product.unit} | estoque atual {physical:.1f} {product.unit}")

    def create_daycare_stay(self):
        try:
            start = datetime.strptime(f"{self.daycare_date_var.get()} {self.daycare_start_var.get()}", "%d/%m/%Y %H:%M")
            end = datetime.strptime(f"{self.daycare_date_var.get()} {self.daycare_end_var.get()}", "%d/%m/%Y %H:%M")
        except ValueError:
            messagebox.showerror("Data invalida", "Use data dd/mm/aaaa e hora hh:mm.")
            return

        if end <= start:
            messagebox.showerror("Horario invalido", "A saida prevista deve ser depois da entrada.")
            return

        if not self.daycare_tutor_var.get().strip() or not self.daycare_pet_var.get().strip():
            messagebox.showerror("Campos obrigatorios", "Informe tutor e pet.")
            return

        active_same_pet = any(
            stay.pet.lower() == self.daycare_pet_var.get().strip().lower()
            and stay.status == "Na creche"
            for stay in self.store.daycare_stays
        )
        if active_same_pet:
            messagebox.showerror("Pet ja registrado", "Este pet ja esta com entrada ativa na creche.")
            return

        stay = DaycareStay(
            id=self.store.next_daycare_id(),
            tutor=self.daycare_tutor_var.get().strip(),
            pet=self.daycare_pet_var.get().strip(),
            breed=self.daycare_breed_var.get(),
            date=self.daycare_date_var.get(),
            start_time=self.daycare_start_var.get(),
            end_time=self.daycare_end_var.get(),
            caregiver=self.daycare_caregiver_var.get(),
            plan=self.daycare_plan_var.get(),
            price=DAYCARE_PLANS[self.daycare_plan_var.get()][BREEDS[self.daycare_breed_var.get()][0]],
            notes=self.daycare_notes_var.get().strip(),
        )
        self.store.daycare_stays.append(stay)
        self.store.save()
        self.refresh_all()
        messagebox.showinfo("Creche", "Entrada registrada com sucesso.")

    def finish_daycare_stay(self):
        stay_id = self.selected_daycare_id()
        if stay_id is None:
            return

        stay = self.find_daycare_stay(stay_id)
        if stay is None:
            return

        stay.status = "Saiu"
        stay.end_time = datetime.now().strftime("%H:%M")
        self.store.save()
        self.refresh_all()
        messagebox.showinfo("Creche", f"Saida registrada para {stay.pet}.")

    def select_operation(self):
        selected = self.operation_list.curselection()
        if not selected:
            return
        appointment_id = int(self.operation_list.get(selected[0]).split(" - ")[0])
        appointment = self.find_appointment(appointment_id)
        self.selected_appointment_id = appointment_id
        if appointment_id not in self.appointment_timers:
            self.appointment_timers[appointment_id] = appointment.duration * 60
        self.countdown_seconds = self.appointment_timers[appointment_id]
        self.timer_running = appointment_id in self.running_timers
        self.operation_selected_var.set(
            f"{appointment.pet} | {appointment.service} | {appointment.duration} min | {appointment.employee}"
        )
        self.update_timer_label()

    def start_timer(self):
        if self.selected_appointment_id is None:
            messagebox.showwarning("Selecao obrigatoria", "Selecione um servico.")
            return
        appointment_id = self.selected_appointment_id
        if appointment_id in self.running_timers:
            return
        if appointment_id not in self.appointment_timers:
            appointment = self.find_appointment(appointment_id)
            self.appointment_timers[appointment_id] = appointment.duration * 60
        self.running_timers.add(appointment_id)
        self.timer_running = True
        self.tick_timer(appointment_id)

    def pause_timer(self):
        if self.selected_appointment_id is None:
            return
        self.running_timers.discard(self.selected_appointment_id)
        self.timer_running = False

    def tick_timer(self, appointment_id):
        if appointment_id not in self.running_timers:
            return
        if appointment_id not in self.appointment_timers:
            return

        if self.appointment_timers[appointment_id] > 0:
            self.appointment_timers[appointment_id] -= 1
            if self.selected_appointment_id == appointment_id:
                self.countdown_seconds = self.appointment_timers[appointment_id]
                self.update_timer_label()
            self.root.after(1000, lambda: self.tick_timer(appointment_id))
        else:
            self.running_timers.discard(appointment_id)
            if self.selected_appointment_id == appointment_id:
                self.timer_running = False
                self.countdown_seconds = 0
                self.update_timer_label()
            messagebox.showinfo("Tempo finalizado", "Tempo padrao do atendimento encerrado.")

    def update_timer_label(self):
        minutes, seconds = divmod(self.countdown_seconds, 60)
        self.timer_var.set(f"{minutes:02d}:{seconds:02d}")

    def finish_service(self):
        if self.selected_appointment_id is None:
            messagebox.showwarning("Selecao obrigatoria", "Selecione um servico.")
            return
        appointment_id = self.selected_appointment_id
        appointment = self.find_appointment(appointment_id)
        if appointment.payment_status != "Confirmado":
            messagebox.showerror("Pagamento pendente", "Finalize apenas servicos com pagamento confirmado.")
            return

        missing = self.store.check_stock_for_service(appointment.service, count_risk=True)
        if missing:
            messagebox.showerror("Estoque insuficiente", "Insumos indisponiveis: " + ", ".join(missing))
            return

        appointment.service_status = "Finalizado"
        appointment.intercorrences = [name for name, var in self.intercurrence_vars.items() if var.get() == "1"]
        used_items = self.store.consume_inputs(appointment.service)
        used_items_text = "\n".join(used_items) if used_items else "Nenhum item baixado."
        self.store.save()
        self.appointment_timers.pop(appointment_id, None)
        self.running_timers.discard(appointment_id)
        self.timer_running = False
        self.selected_appointment_id = None
        self.countdown_seconds = 0
        self.update_timer_label()
        for variable in self.intercurrence_vars.values():
            variable.set("0")
        self.used_items_var.set("Ultimos itens utilizados:\n" + used_items_text)
        self.refresh_all()
        messagebox.showinfo(
            "Servico finalizado",
            "Itens utilizados:\n\n" + used_items_text
        )

    def refresh_all(self):
        self.update_preview()
        self.refresh_agenda()
        self.refresh_stock()
        self.refresh_operation()
        self.refresh_daycare()
        self.refresh_dashboard()
        self.apply_access_without_refresh()

    def apply_access_without_refresh(self):
        allowed = ACCESS[self.current_profile.get()]
        for key, tab in {
            "agenda": self.agenda_tab,
            "estoque": self.stock_tab,
            "operacional": self.operation_tab,
            "creche": self.daycare_tab,
            "dashboard": self.dashboard_tab,
        }.items():
            self.tabs.tab(tab, state="normal" if key in allowed else "disabled")

    def refresh_agenda(self):
        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)
        for appointment in sorted(self.store.appointments, key=lambda item: (item.date, item.start_time)):
            self.appointment_tree.insert(
                "",
                END,
                values=(
                    appointment.id,
                    appointment.date,
                    appointment.start_time,
                    appointment.employee,
                    appointment.pet,
                    appointment.service,
                    f"{appointment.duration}+{appointment.buffer} min",
                    appointment.payment_status,
                    appointment.service_status,
                ),
            )

    def refresh_stock(self):
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        for product in self.store.products:
            status = " CRITICO" if product.stock <= product.critical_level else ""
            self.stock_tree.insert(
                "",
                END,
                values=(
                    product.name + status,
                    product.unit,
                    f"{product.stock:.1f}",
                    f"{product.critical_level:.1f}",
                    f"{product.estimated_usage:.1f}",
                ),
            )

    def refresh_operation(self):
        self.operation_list.delete(0, END)
        for appointment in self.store.appointments:
            if appointment.service_status == "Agendado":
                self.operation_list.insert(
                    END,
                    f"{appointment.id} - {appointment.date} {appointment.start_time} - {appointment.employee} - {appointment.pet} - {appointment.service} - {appointment.payment_status}",
                )

    def refresh_daycare(self):
        for item in self.daycare_tree.get_children():
            self.daycare_tree.delete(item)
        for stay in sorted(self.store.daycare_stays, key=lambda item: (item.date, item.start_time)):
            self.daycare_tree.insert(
                "",
                END,
                values=(
                    stay.id,
                    stay.date,
                    stay.start_time,
                    stay.end_time,
                    stay.caregiver,
                    stay.pet,
                    stay.breed,
                    stay.tutor,
                    stay.plan,
                    f"R$ {stay.price:.2f}",
                    stay.status,
                ),
            )

    def refresh_dashboard(self):
        total_minutes = 10 * 60
        total_team_minutes = total_minutes * len(BATH_GROOMING_EMPLOYEES)
        sold_minutes = sum(
            appointment.duration + appointment.buffer
            for appointment in self.store.appointments
            if appointment.service_status != "Cancelado"
        )
        occupation = min((sold_minutes / total_team_minutes) * 100, 100) if total_team_minutes else 0
        paid = [appointment.price for appointment in self.store.appointments if appointment.payment_status == "Confirmado"]
        average_ticket = sum(paid) / len(paid) if paid else 0
        daycare_revenue = sum(stay.price for stay in self.store.daycare_stays)
        critical_products = [product.name for product in self.store.products if product.stock <= product.critical_level]
        active_daycare = [stay for stay in self.store.daycare_stays if stay.status == "Na creche"]
        daycare_lines = []
        for caregiver in DAYCARE_CAREGIVERS:
            caregiver_total = sum(1 for stay in active_daycare if stay.caregiver == caregiver)
            daycare_lines.append(f"- {caregiver}: {caregiver_total} pet(s) na creche")
        employee_lines = []
        for employee in BATH_GROOMING_EMPLOYEES:
            employee_minutes = sum(
                appointment.duration + appointment.buffer
                for appointment in self.store.appointments
                if appointment.employee == employee and appointment.service_status != "Cancelado"
            )
            employee_occupation = min((employee_minutes / total_minutes) * 100, 100) if total_minutes else 0
            employee_lines.append(f"- {employee}: {employee_occupation:.1f}% ocupado ({employee_minutes} min bloqueados)")

        text = (
            "KPIs DE PERFORMANCE\n\n"
            "Equipe cadastrada:\n"
            f"- Gestao: {', '.join(MANAGEMENT_TEAM)}\n"
            f"- Banho e tosa: {', '.join(BATH_GROOMING_EMPLOYEES)}\n"
            f"- Creche: {', '.join(DAYCARE_CAREGIVERS)}\n"
            f"- Total operacional informado: {len(MANAGEMENT_TEAM) + len(BATH_GROOMING_EMPLOYEES) + len(DAYCARE_CAREGIVERS)} pessoas\n\n"
            f"Taxa de ocupacao: {occupation:.1f}% do dia comercial padrao\n"
            f"Ruptura de estoque: {self.store.stock_break_risks} risco(s) registrado(s)\n"
            f"Ticket medio: R$ {average_ticket:.2f}\n\n"
            f"Receita prevista da creche: R$ {daycare_revenue:.2f}\n"
            "Ocupacao banho/tosa:\n"
            f"{os.linesep.join(employee_lines)}\n\n"
            f"Pets ativos na creche: {len(active_daycare)}\n"
            "Distribuicao da creche:\n"
            f"{os.linesep.join(daycare_lines)}\n\n"
            "Alertas de estoque critico:\n"
            f"{', '.join(critical_products) if critical_products else 'Nenhum produto em nivel critico'}\n\n"
            "Regras ativas:\n"
            "- Tempo travado por raca/porte\n"
            "- Buffer sanitario de 15 minutos\n"
            "- Conflito parcial bloqueado por funcionario\n"
            "- Baixa automatica de insumos ao finalizar servico\n"
            "- Novo agendamento bloqueado quando ha pagamento pendente"
        )
        self.dashboard_text.configure(state="normal")
        self.dashboard_text.delete("1.0", END)
        self.dashboard_text.insert("1.0", text)
        self.dashboard_text.configure(state="disabled")


def main():
    os.chdir(Path(__file__).parent)
    root = Tk()
    PetShopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
