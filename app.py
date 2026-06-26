from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Sistema Loja de Carros", layout="wide")

VEHICLE_STATUS = ["Disponivel", "Reservado", "Vendido"]
PROPOSAL_STATUS = ["Aberta", "Aceita", "Recusada", "Cancelada"]
PAYMENT_METHODS = ["A vista", "Financiamento", "Troca + volta", "Consorcio"]


def money(value: Any) -> str:
    value = float(value or 0)
    formatted = f"R$ {value:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def secret(name: str) -> str:
    try:
        return st.secrets.get(name, "")
    except Exception:
        return ""


def supabase_config() -> tuple[str, str]:
    url = secret("SUPABASE_URL")
    key = secret("SUPABASE_ANON_KEY")
    return url.rstrip("/"), key


def supabase_headers(prefer: str | None = None) -> dict[str, str]:
    _, key = supabase_config()
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def supabase_request(method: str, table: str, **kwargs):
    url, _ = supabase_config()
    response = requests.request(
        method,
        f"{url}/rest/v1/{table}",
        headers=supabase_headers(kwargs.pop("prefer", None)),
        timeout=20,
        **kwargs,
    )
    response.raise_for_status()
    if response.content:
        return response.json()
    return None


def init_demo_data() -> None:
    st.session_state.setdefault(
        "vehicles",
        [
            {
                "id": "demo-vehicle-1",
                "brand": "Toyota",
                "model": "Corolla XEi",
                "year": 2021,
                "color": "Prata",
                "mileage": 48500,
                "plate": "ABC1D23",
                "chassis": "9BR00000000000001",
                "purchase_price": 94000,
                "sale_price": 112900,
                "status": "Disponivel",
                "notes": "Unico dono, revisoes em dia.",
                "created_at": str(date.today()),
            },
            {
                "id": "demo-vehicle-2",
                "brand": "Hyundai",
                "model": "HB20 Comfort",
                "year": 2020,
                "color": "Branco",
                "mileage": 61200,
                "plate": "XYZ9A88",
                "chassis": "9BH00000000000002",
                "purchase_price": 51500,
                "sale_price": 62900,
                "status": "Reservado",
                "notes": "Cliente aguardando financiamento.",
                "created_at": str(date.today()),
            },
        ],
    )
    st.session_state.setdefault(
        "vehicle_photos",
        [
            {
                "id": "demo-photo-1",
                "vehicle_id": "demo-vehicle-1",
                "photo_url": "https://images.unsplash.com/photo-1626072778346-0ab6604d39d1?auto=format&fit=crop&w=900&q=80",
                "created_at": str(date.today()),
            }
        ],
    )
    st.session_state.setdefault(
        "customers",
        [
            {
                "id": "demo-customer-1",
                "name": "Marcos Silva",
                "phone": "(11) 99999-0000",
                "email": "marcos@email.com",
                "document": "",
                "notes": "Procura sedan automatico.",
                "created_at": str(date.today()),
            }
        ],
    )
    st.session_state.setdefault("proposals", [])
    st.session_state.setdefault("sales", [])
    st.session_state.setdefault(
        "expenses",
        [
            {
                "id": "demo-expense-1",
                "vehicle_id": "demo-vehicle-1",
                "description": "Polimento e higienizacao",
                "amount": 850,
                "expense_date": str(date.today()),
                "created_at": str(date.today()),
            }
        ],
    )


def is_demo() -> bool:
    url, key = supabase_config()
    return not url or not key


def list_rows(table: str) -> list[dict[str, Any]]:
    if is_demo():
        init_demo_data()
        return list(st.session_state[table])
    result = supabase_request("GET", table, params={"select": "*", "order": "created_at.desc"})
    return result or []


def insert_row(table: str, row: dict[str, Any]) -> None:
    if is_demo():
        init_demo_data()
        st.session_state[table].insert(0, {"id": str(uuid4()), "created_at": str(date.today())} | row)
        return
    supabase_request("POST", table, json=row, prefer="return=minimal")


def update_row(table: str, row_id: str, values: dict[str, Any]) -> None:
    if is_demo():
        init_demo_data()
        st.session_state[table] = [
            item | values if item["id"] == row_id else item for item in st.session_state[table]
        ]
        return
    supabase_request("PATCH", table, params={"id": f"eq.{row_id}"}, json=values, prefer="return=minimal")


def vehicle_name(vehicle: dict[str, Any]) -> str:
    return f"{vehicle['brand']} {vehicle['model']} {vehicle['year']} - {vehicle['plate']}"


def vehicle_options() -> dict[str, str]:
    return {vehicle_name(vehicle): vehicle["id"] for vehicle in list_rows("vehicles")}


def customer_options() -> dict[str, str]:
    return {customer["name"]: customer["id"] for customer in list_rows("customers")}


def to_df(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def top_bar() -> None:
    st.title("Sistema da Loja de Carros")
    st.caption("Veiculos, fotos, clientes, propostas, vendas, despesas e lucro por carro.")
    if is_demo():
        st.info("Modo demo ativo. Configure o Supabase em .streamlit/secrets.toml para salvar no banco.")


def dashboard() -> None:
    vehicles = list_rows("vehicles")
    expenses = list_rows("expenses")
    sales = list_rows("sales")

    available = [vehicle for vehicle in vehicles if vehicle["status"] == "Disponivel"]
    reserved = [vehicle for vehicle in vehicles if vehicle["status"] == "Reservado"]
    sold = [vehicle for vehicle in vehicles if vehicle["status"] == "Vendido"]
    inventory_value = sum(float(vehicle.get("sale_price") or 0) for vehicle in available + reserved)
    total_expenses = sum(float(expense.get("amount") or 0) for expense in expenses)
    total_sales = sum(float(sale.get("sale_price") or 0) for sale in sales)

    cols = st.columns(5)
    cols[0].metric("Disponiveis", len(available))
    cols[1].metric("Reservados", len(reserved))
    cols[2].metric("Vendidos", len(sold))
    cols[3].metric("Estoque anunciado", money(inventory_value))
    cols[4].metric("Vendas registradas", money(total_sales))

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Veiculos por status")
        chart_data = to_df(vehicles)
        if chart_data.empty:
            st.write("Nenhum veiculo cadastrado.")
        else:
            st.bar_chart(chart_data.groupby("status").size().reset_index(name="quantidade"), x="status", y="quantidade")
    with right:
        st.subheader("Despesas recentes")
        st.metric("Total gasto em preparacao", money(total_expenses))
        if expenses:
            latest = to_df(expenses).head(5)
            latest["amount"] = latest["amount"].apply(money)
            st.dataframe(latest[["description", "amount", "expense_date"]], use_container_width=True, hide_index=True)


def vehicles_page() -> None:
    st.subheader("Cadastro de veiculos")
    with st.form("vehicle_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        brand = c1.text_input("Marca")
        model = c2.text_input("Modelo")
        year = c3.number_input("Ano", min_value=1950, max_value=2040, value=2020)
        color = c4.text_input("Cor")

        c1, c2, c3, c4 = st.columns(4)
        mileage = c1.number_input("Km", min_value=0, value=0, step=500)
        plate = c2.text_input("Placa")
        chassis = c3.text_input("Chassi")
        status = c4.selectbox("Status", VEHICLE_STATUS)

        c1, c2 = st.columns(2)
        purchase_price = c1.number_input("Preco de compra", min_value=0.0, step=500.0)
        sale_price = c2.number_input("Preco de venda", min_value=0.0, step=500.0)
        photo_urls = st.text_area("Fotos do carro", help="Cole uma URL por linha.")
        notes = st.text_area("Observacoes")

        if st.form_submit_button("Salvar veiculo", type="primary"):
            vehicle_id = str(uuid4())
            row = {
                "brand": brand,
                "model": model,
                "year": int(year),
                "color": color,
                "mileage": int(mileage),
                "plate": plate.upper(),
                "chassis": chassis.upper(),
                "purchase_price": float(purchase_price),
                "sale_price": float(sale_price),
                "status": status,
                "notes": notes,
            }
            if vehicle_id:
                row["id"] = vehicle_id
            insert_row("vehicles", row)
            if photo_urls:
                for url in [line.strip() for line in photo_urls.splitlines() if line.strip()]:
                    insert_row("vehicle_photos", {"vehicle_id": vehicle_id, "photo_url": url})
            st.success("Veiculo salvo.")
            st.rerun()

    rows = list_rows("vehicles")
    photos = list_rows("vehicle_photos")
    if rows:
        table = to_df(rows)
        for col in ["purchase_price", "sale_price"]:
            table[col] = table[col].apply(money)
        st.dataframe(table, use_container_width=True, hide_index=True)

        st.subheader("Fotos cadastradas")
        for vehicle in rows:
            vehicle_photos = [photo for photo in photos if photo["vehicle_id"] == vehicle["id"]]
            if vehicle_photos:
                st.write(vehicle_name(vehicle))
                st.image([photo["photo_url"] for photo in vehicle_photos], width=180)

        st.subheader("Atualizar status")
        options = vehicle_options()
        selected = st.selectbox("Veiculo", list(options.keys()))
        new_status = st.selectbox("Novo status", VEHICLE_STATUS)
        if st.button("Atualizar status", type="primary"):
            update_row("vehicles", options[selected], {"status": new_status})
            st.success("Status atualizado.")
            st.rerun()


def customers_page() -> None:
    st.subheader("Cadastro de clientes")
    with st.form("customer_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Nome")
        phone = c2.text_input("Telefone/WhatsApp")
        c1, c2 = st.columns(2)
        email = c1.text_input("E-mail")
        document = c2.text_input("CPF/CNPJ")
        notes = st.text_area("Observacoes")
        if st.form_submit_button("Salvar cliente", type="primary"):
            insert_row("customers", {"name": name, "phone": phone, "email": email, "document": document, "notes": notes})
            st.success("Cliente salvo.")
            st.rerun()

    rows = list_rows("customers")
    if rows:
        st.dataframe(to_df(rows), use_container_width=True, hide_index=True)


def proposals_page() -> None:
    st.subheader("Registro de propostas")
    vehicles = vehicle_options()
    customers = customer_options()
    if not vehicles or not customers:
        st.warning("Cadastre pelo menos um veiculo e um cliente antes de registrar proposta.")
        return

    with st.form("proposal_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        vehicle_label = c1.selectbox("Veiculo", list(vehicles.keys()))
        customer_label = c2.selectbox("Cliente", list(customers.keys()))
        c1, c2, c3 = st.columns(3)
        proposed_price = c1.number_input("Valor proposto", min_value=0.0, step=500.0)
        payment_method = c2.selectbox("Forma de pagamento", PAYMENT_METHODS)
        status = c3.selectbox("Status", PROPOSAL_STATUS)
        notes = st.text_area("Observacoes")
        if st.form_submit_button("Salvar proposta", type="primary"):
            insert_row(
                "proposals",
                {
                    "vehicle_id": vehicles[vehicle_label],
                    "customer_id": customers[customer_label],
                    "proposed_price": float(proposed_price),
                    "payment_method": payment_method,
                    "status": status,
                    "notes": notes,
                },
            )
            st.success("Proposta salva.")
            st.rerun()

    rows = list_rows("proposals")
    if rows:
        table = to_df(rows)
        table["proposed_price"] = table["proposed_price"].apply(money)
        st.dataframe(table, use_container_width=True, hide_index=True)


def sales_page() -> None:
    st.subheader("Registro de vendas")
    vehicles = vehicle_options()
    customers = customer_options()
    if not vehicles or not customers:
        st.warning("Cadastre pelo menos um veiculo e um cliente antes de registrar venda.")
        return

    with st.form("sale_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        vehicle_label = c1.selectbox("Veiculo vendido", list(vehicles.keys()))
        customer_label = c2.selectbox("Cliente comprador", list(customers.keys()))
        c1, c2 = st.columns(2)
        sale_price = c1.number_input("Valor da venda", min_value=0.0, step=500.0)
        sale_date = c2.date_input("Data da venda")
        notes = st.text_area("Observacoes")
        if st.form_submit_button("Registrar venda", type="primary"):
            insert_row(
                "sales",
                {
                    "vehicle_id": vehicles[vehicle_label],
                    "customer_id": customers[customer_label],
                    "sale_price": float(sale_price),
                    "sale_date": str(sale_date),
                    "notes": notes,
                },
            )
            update_row("vehicles", vehicles[vehicle_label], {"status": "Vendido"})
            st.success("Venda registrada e veiculo marcado como vendido.")
            st.rerun()

    rows = list_rows("sales")
    if rows:
        table = to_df(rows)
        table["sale_price"] = table["sale_price"].apply(money)
        st.dataframe(table, use_container_width=True, hide_index=True)


def expenses_page() -> None:
    st.subheader("Controle de despesas por veiculo")
    vehicles = vehicle_options()
    if not vehicles:
        st.warning("Cadastre um veiculo antes de registrar despesas.")
        return

    with st.form("expense_form", clear_on_submit=True):
        vehicle_label = st.selectbox("Veiculo", list(vehicles.keys()))
        c1, c2 = st.columns(2)
        description = c1.text_input("Descricao")
        amount = c2.number_input("Valor", min_value=0.0, step=100.0)
        expense_date = st.date_input("Data")
        if st.form_submit_button("Salvar despesa", type="primary"):
            insert_row(
                "expenses",
                {
                    "vehicle_id": vehicles[vehicle_label],
                    "description": description,
                    "amount": float(amount),
                    "expense_date": str(expense_date),
                },
            )
            st.success("Despesa salva.")
            st.rerun()

    rows = list_rows("expenses")
    if rows:
        table = to_df(rows)
        table["amount"] = table["amount"].apply(money)
        st.dataframe(table, use_container_width=True, hide_index=True)


def profit_report_page() -> None:
    st.subheader("Relatorio de lucro por carro")
    vehicles = list_rows("vehicles")
    expenses = list_rows("expenses")
    sales = list_rows("sales")
    rows = []
    for vehicle in vehicles:
        vehicle_id = vehicle["id"]
        vehicle_expenses = sum(float(expense.get("amount") or 0) for expense in expenses if expense.get("vehicle_id") == vehicle_id)
        sale = next((item for item in sales if item.get("vehicle_id") == vehicle_id), None)
        sale_price = float((sale or {}).get("sale_price") or 0)
        purchase_price = float(vehicle.get("purchase_price") or 0)
        revenue_basis = sale_price if sale else float(vehicle.get("sale_price") or 0)
        profit = revenue_basis - purchase_price - vehicle_expenses
        rows.append(
            {
                "veiculo": vehicle_name(vehicle),
                "status": vehicle["status"],
                "compra": purchase_price,
                "venda_real_ou_anunciada": revenue_basis,
                "despesas": vehicle_expenses,
                "lucro": profit,
            }
        )

    if not rows:
        st.write("Nenhum veiculo cadastrado.")
        return

    table = to_df(rows)
    st.metric("Lucro total estimado/real", money(table["lucro"].sum()))
    for col in ["compra", "venda_real_ou_anunciada", "despesas", "lucro"]:
        table[col] = table[col].apply(money)
    st.dataframe(table, use_container_width=True, hide_index=True)


def settings_page() -> None:
    st.subheader("Supabase")
    st.write("Crie `.streamlit/secrets.toml` com:")
    st.code(
        'SUPABASE_URL = "https://seu-projeto.supabase.co"\nSUPABASE_ANON_KEY = "sua-chave-anon-publica"',
        language="toml",
    )
    st.write("Depois rode o arquivo `supabase_schema.sql` no SQL Editor do Supabase.")


def main() -> None:
    top_bar()
    page = st.sidebar.radio(
        "Menu",
        [
            "Painel",
            "Veiculos",
            "Clientes",
            "Propostas",
            "Vendas",
            "Despesas",
            "Lucro por carro",
            "Configuracao",
        ],
    )
    pages = {
        "Painel": dashboard,
        "Veiculos": vehicles_page,
        "Clientes": customers_page,
        "Propostas": proposals_page,
        "Vendas": sales_page,
        "Despesas": expenses_page,
        "Lucro por carro": profit_report_page,
        "Configuracao": settings_page,
    }
    pages[page]()


if __name__ == "__main__":
    main()
