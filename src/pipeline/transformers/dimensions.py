import pandas as pd
import logging
import functools
from ..config import TENANT_ID_BASES

logger = logging.getLogger(__name__)

def requires_dataframe(fn):
    @functools.wraps(fn)
    def wrapper(df, *args, **kwargs):
        if df is None or df.empty:
            logger.warning(f"Skipping {fn.__name__}: no input data")
            return None
        return fn(df, *args, **kwargs)
    return wrapper

@requires_dataframe
def build_dim_date(orders_df: pd.DataFrame) -> pd.DataFrame:
    dates = orders_df[['orderDate']].drop_duplicates().copy()
    dt = pd.to_datetime(dates['orderDate'])
    
    dates['date_id'] = dt.dt.strftime('%Y%m%d').astype(int)
    dates['full_date'] = dt.dt.date
    dates['year'] = dt.dt.year
    dates['month'] = dt.dt.month
    dates['day'] = dt.dt.day
    dates['day_name'] = dt.dt.day_name()
    dates['quarter'] = dt.dt.quarter
    
    dim_date = dates[['date_id','full_date','year','month','day','day_name','quarter']].drop_duplicates()
    return dim_date

@requires_dataframe
def build_dim_product(product_df: pd.DataFrame) -> pd.DataFrame:
    df = product_df.sort_values('product_id').drop_duplicates(subset=['tenant_id', 'product_id'], keep='last').copy()
    idx = df.groupby('tenant_id').cumcount() + 1
    df['product_id'] = df['tenant_id'].map(TENANT_ID_BASES["product"]) + idx
    
    dim_product = df[['tenant_id','product_id','name','category','base_price','tax_percent']].copy()
    dim_product.columns = ['tenant_id','product_id','name','category','base_price','tax_percentage']
    return dim_product

@requires_dataframe
def build_dim_customer(customer_df: pd.DataFrame) -> pd.DataFrame:
    required_cols = ['tenant_id', 'customer_id', 'segment', 'city', 'customer_type']
    missing_cols = [col for col in required_cols if col not in customer_df.columns]
    if missing_cols:
        logger.error(f"Missing columns in customer_df: {missing_cols}")
        logger.info(f"Available columns: {list(customer_df.columns)}")
        return None
    
    df = customer_df.sort_values('customer_id').drop_duplicates(subset=['tenant_id', 'customer_id'], keep='last').copy()
    idx = df.groupby('tenant_id').cumcount() + 1
    df['customer_id'] = df['tenant_id'].map(TENANT_ID_BASES["customer"]) + idx
    
    dim_customer = df[required_cols].copy()
    dim_customer.columns = required_cols
    return dim_customer

@requires_dataframe
def build_dim_employee(employee_df: pd.DataFrame) -> pd.DataFrame:
    df = employee_df.sort_values('employee_id').drop_duplicates(subset=['tenant_id', 'employee_id'], keep='last').copy()
    idx = df.groupby('tenant_id').cumcount() + 1
    df['employee_id'] = df['tenant_id'].map(TENANT_ID_BASES["employee"]) + idx
    
    dim_employee = df[['tenant_id','employee_id','position','branch_id']].copy()
    dim_employee.columns = ['tenant_id','employee_id','position','sectional_id']
    return dim_employee

@requires_dataframe
def build_dim_sectional(branch_df: pd.DataFrame) -> pd.DataFrame:
    df = branch_df.sort_values('branch_id').drop_duplicates(subset=['tenant_id', 'branch_id'], keep='last').copy()
    idx = df.groupby('tenant_id').cumcount() + 1
    df['branch_id'] = df['tenant_id'].map(TENANT_ID_BASES["sectional"]) + idx
    
    dim_sectional = df[['tenant_id','branch_id','name','city']].copy()
    dim_sectional.columns = ['tenant_id','sectional_id','name','city']
    return dim_sectional

@requires_dataframe
def build_dim_payment_method(payment_method_df: pd.DataFrame) -> pd.DataFrame:
    dim_payment_method = payment_method_df[['method_id','name','type']].copy()
    dim_payment_method.columns = ['method_id','name','type']
    return dim_payment_method

def build_fact_sales(order_lines_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
    if order_lines_df is None or order_lines_df.empty or orders_df is None or orders_df.empty:
        logger.warning("Skipping build_fact_sales: Missing order_lines_df or orders_df")
        return None
        
    paid_lines = order_lines_df[order_lines_df['eventType'] == 'paid'].copy()
    if paid_lines.empty:
        logger.warning("No paid order lines found")
        return None
        
    fact = paid_lines.merge(orders_df, on=['tenant_id','orderId'], how='left', suffixes=('','_order'))

    fact['subtotal'] = fact['quantity'] * fact['unitPrice'] - fact['discount']
    fact['tax'] = fact['subtotal'] * fact['taxRate']
    fact['total_line'] = fact['subtotal'] + fact['tax']

    fact['date_id'] = pd.to_datetime(fact['orderDate']).dt.strftime('%Y%m%d').astype(int)
    fact['line_id'] = pd.to_numeric(fact['lineId'], errors='coerce').fillna(0).astype('int64')
    fact['invoice_id'] = pd.to_numeric(fact['orderId'].str.extract(r'(\d+)')[0], errors='coerce').fillna(0).astype('int32')

    fact_final = fact[[
        'tenant_id', 'line_id', 'invoice_id', 'date_id',
        'productId', 'customerId', 'employeeId', 'branchId', 'paymentMethodId',
        'quantity', 'unitPrice', 'subtotal', 'tax', 'discount', 'total_line'
    ]].rename(columns={
        'productId': 'product_id',
        'customerId': 'customer_id',
        'employeeId': 'employee_id',
        'branchId': 'sectional_id',
        'paymentMethodId': 'payment_method_id',
        'quantity': 'quantity',
        'unitPrice': 'unit_price',
        'discount': 'discount'
    })

    fact_final['line_id'] = fact_final['line_id'].astype('int64')
    fact_final['invoice_id'] = fact_final['invoice_id'].astype('int32')
    fact_final['date_id'] = fact_final['date_id'].astype('int32')
    fact_final['product_id'] = fact_final['product_id'].astype('int32')
    fact_final['customer_id'] = fact_final['customer_id'].astype('int32')
    fact_final['employee_id'] = fact_final['employee_id'].astype('int32')
    fact_final['sectional_id'] = fact_final['sectional_id'].astype('int32')
    fact_final['payment_method_id'] = fact_final['payment_method_id'].astype('int8')

    return fact_final