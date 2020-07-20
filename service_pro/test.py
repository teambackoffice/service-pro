import frappe
from erpnext.stock.utils import get_latest_stock_qty,get_stock_value_from_bin,get_stock_value_on,get_stock_balance

def get_qty():
    # BLV - 0061
    print(get_stock_balance("BLV-0061", "Work In Progress - HYDROTECH"))