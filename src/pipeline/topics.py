from .transformers.dimensions import (
    build_dim_customer, build_fact_sales, build_dim_sectional, 
    build_dim_employee, build_dim_product, build_dim_date, 
    build_dim_payment_method
)
from dataclasses import dataclass
from typing import Dict
from typing import Callable, Optional
import pandas as pd

@dataclass
class TopicConfig:
    display_name: str
    topic: str  

@dataclass
class TableConfig:
    table: str 
    dependencies: list[str] 
    builder_func: Callable[..., Optional[pd.DataFrame]]

TOPICS: Dict[str, TopicConfig] = {
    "category": TopicConfig(
        display_name="Categorías",
        topic="product-db.product_database.category"
    ),
    "product": TopicConfig(
        display_name="Productos",
        topic="product-db.product_database.product"
    ),
    "order_lines": TopicConfig(
        display_name="Líneas de pedido",
        topic="sales-db.sales_database.orderLines"
    ),
    "orders": TopicConfig(
        display_name="Pedidos",
        topic="sales-db.sales_database.orders"
    ),
    "branch": TopicConfig(
        display_name="Sucursales",
        topic="user-db.user_database.branch"
    ),
    "customer": TopicConfig(
        display_name="Clientes",
        topic="user-db.user_database.customer"
    ),
    "employee": TopicConfig(
        display_name="Empleados",
        topic="user-db.user_database.employee"
    ),
    "payment_method": TopicConfig(
        display_name="Métodos de pago",
        topic="user-db.user_database.payment_method"
    ),
}

TRANSFORMATIONS : list[TableConfig] = [
    TableConfig(
        table="dim_date",
        dependencies=["orders"],
        builder_func=build_dim_date
    ),
    TableConfig(
        table="dim_product",
        dependencies=["product"],
        builder_func=build_dim_product
    ),
    TableConfig(
        table="dim_customer",
        dependencies=["customer"],
        builder_func=build_dim_customer
    ),
    TableConfig(
        table="dim_employee",
        dependencies=["employee"],
        builder_func=build_dim_employee
    ),
    TableConfig(
        table="dim_sectional",
        dependencies=["branch"],
        builder_func=build_dim_sectional
    ),
    TableConfig(
        table="dim_payment_method",
        dependencies=["payment_method"],
        builder_func=build_dim_payment_method
    ),
    TableConfig(
        table="fact_sales_line",
        dependencies=["order_lines", "orders"],
        builder_func=build_fact_sales
    ),
]


