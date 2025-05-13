from operator import itemgetter
from typing import Any, TypedDict
import functools

import frappe
from frappe import _
from frappe.query_builder import Order
from frappe.query_builder.functions import Coalesce
from frappe.utils import add_days, cint, date_diff, flt, getdate
from frappe.utils.nestedset import get_descendants_of

import erpnext
from erpnext.stock.doctype.inventory_dimension.inventory_dimension import get_inventory_dimensions
from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter


class StockBalanceFilter(TypedDict):
    company: str | None
    from_date: str
    to_date: str
    item_group: str | None
    item: str | None
    warehouse: str | None
    warehouse_type: str | None
    include_uom: str | None
    show_stock_ageing_data: bool
    show_variant_attributes: bool


SLEntry = dict[str, Any]


def execute(filters: StockBalanceFilter | None = None):
    return CustomStockBalanceReport(filters).run()


class CustomStockBalanceReport:
    def __init__(self, filters: StockBalanceFilter | None) -> None:
        self.filters = filters
        self.from_date = getdate(filters.get("from_date"))
        self.to_date = getdate(filters.get("to_date"))
        self.start_from = None
        self.data = []
        self.columns = []
        self.sle_entries: list[SLEntry] = []
        self.set_company_currency()
        self.warehouses = set(self.get_all_warehouses())

    def set_company_currency(self) -> None:
        self.company_currency = (
            erpnext.get_company_currency(self.filters.get("company"))
            if self.filters.get("company")
            else frappe.db.get_single_value("Global Defaults", "default_currency")
        )

    def get_all_warehouses(self):
        return ["Stores - HCCW", "Stores - HTCD", "Stores - HTCJ", "Stores - HTCR"]

    def run(self):
        self.float_precision = cint(frappe.db.get_default("float_precision")) or 3
        self.inventory_dimensions = self.get_inventory_dimension_fields()
        self.prepare_opening_data_from_closing_balance()
        self.prepare_stock_ledger_entries()
        self.prepare_consolidated_data()
        self.columns = self.get_columns_with_warehouse_balances()
        return self.columns, self.data

    def prepare_opening_data_from_closing_balance(self):
        self.opening_data = frappe._dict()
        closing_balance = self.get_closing_balance()
        if not closing_balance:
            return

        self.start_from = add_days(closing_balance[0].to_date, 1)
        res = frappe.get_doc("Closing Stock Balance", closing_balance[0].name).get_prepared_data()

        for entry in res.data:
            entry = frappe._dict(entry)
            group_by_key = (entry.item_code, entry.warehouse)
            if group_by_key not in self.opening_data:
                self.opening_data.setdefault(group_by_key, entry)

    def prepare_consolidated_data(self):
        item_warehouse_map = self.get_item_warehouse_map()
        consolidated_items = {}

        for key, data in item_warehouse_map.items():
            item_code, warehouse = data.item_code, data.warehouse
            if warehouse not in self.warehouses:
                continue

            if item_code not in consolidated_items:
                consolidated_items[item_code] = {
                    "item_code": item_code,
                    "item_name": data.item_name,
                    "item_group": data.item_group,
                    "stock_uom": data.stock_uom,
                    "bal_qty": 0,
                    "bal_val": 0,
                    "currency": self.company_currency,
                }
                for wh in self.warehouses:
                    consolidated_items[item_code][f"{wh}_bal_qty"] = 0
                    consolidated_items[item_code][f"{wh}_bal_val"] = 0

            consolidated_items[item_code][f"{warehouse}_bal_qty"] = flt(data.bal_qty)
            consolidated_items[item_code][f"{warehouse}_bal_val"] = flt(data.bal_val)
            consolidated_items[item_code]["bal_qty"] += flt(data.bal_qty)
            consolidated_items[item_code]["bal_val"] += flt(data.bal_val)

        self.data = list(consolidated_items.values())

    def get_item_warehouse_map(self):
        item_warehouse_map = {}
        self.opening_vouchers = self.get_opening_vouchers()
        self.sle_entries = self.sle_query.run(as_dict=True, as_iterator=not self.filters.get("show_stock_ageing_data"))

        for entry in self.sle_entries:
            group_by_key = (entry.item_code, entry.warehouse)
            if group_by_key not in item_warehouse_map:
                self.initialize_data(item_warehouse_map, group_by_key, entry)
            self.prepare_item_warehouse_map(item_warehouse_map, entry, group_by_key)
            self.opening_data.pop(group_by_key, None)

        for group_by_key, entry in self.opening_data.items():
            if group_by_key not in item_warehouse_map:
                self.initialize_data(item_warehouse_map, group_by_key, entry)

        return filter_items_with_no_transactions(item_warehouse_map, self.float_precision, self.inventory_dimensions)

    def prepare_item_warehouse_map(self, item_warehouse_map, entry, group_by_key):
        qty_dict = item_warehouse_map[group_by_key]
        for field in self.inventory_dimensions:
            qty_dict[field] = entry.get(field)

        qty_diff = flt(entry.qty_after_transaction) - flt(qty_dict.bal_qty) if entry.voucher_type == "Stock Reconciliation" and (not entry.batch_no or entry.serial_no) else flt(entry.actual_qty)
        value_diff = flt(entry.stock_value_difference)

        if entry.posting_date < self.from_date or entry.voucher_no in self.opening_vouchers.get(entry.voucher_type, []):
            qty_dict.opening_qty += qty_diff
            qty_dict.opening_val += value_diff
        elif self.from_date <= entry.posting_date <= self.to_date:
            if qty_diff >= 0:
                qty_dict.in_qty += qty_diff
                qty_dict.in_val += value_diff
            else:
                qty_dict.out_qty += abs(qty_diff)
                qty_dict.out_val += abs(value_diff)

        qty_dict.val_rate = entry.valuation_rate
        qty_dict.bal_qty += qty_diff
        qty_dict.bal_val += value_diff

    def initialize_data(self, item_warehouse_map, group_by_key, entry):
        opening_data = self.opening_data.get(group_by_key, {})
        item_warehouse_map[group_by_key] = frappe._dict({
            "item_code": entry.item_code,
            "warehouse": entry.warehouse,
            "item_group": entry.item_group,
            "company": entry.company,
            "currency": self.company_currency,
            "stock_uom": entry.stock_uom,
            "item_name": entry.item_name,
            "opening_qty": opening_data.get("bal_qty", 0.0),
            "opening_val": opening_data.get("bal_val", 0.0),
            "opening_fifo_queue": opening_data.get("fifo_queue", []),
            "in_qty": 0.0, "in_val": 0.0,
            "out_qty": 0.0, "out_val": 0.0,
            "bal_qty": opening_data.get("bal_qty", 0.0),
            "bal_val": opening_data.get("bal_val", 0.0),
            "val_rate": 0.0,
        })

    def get_closing_balance(self):
        if self.filters.get("ignore_closing_balance"):
            return []

        table = frappe.qb.DocType("Closing Stock Balance")
        query = (
            frappe.qb.from_(table)
            .select(table.name, table.to_date)
            .where((table.docstatus == 1) & (table.company == self.filters.company) & (table.to_date <= self.from_date) & (table.status == "Completed"))
            .orderby(table.to_date, order=Order.desc)
            .limit(1)
        )
        for field in ["warehouse", "item_code", "item_group", "warehouse_type"]:
            if self.filters.get(field):
                query = query.where(table[field] == self.filters.get(field))
        return query.run(as_dict=True)

    def prepare_stock_ledger_entries(self):
        sle, item_table = frappe.qb.DocType("Stock Ledger Entry"), frappe.qb.DocType("Item")
        query = (
            frappe.qb.from_(sle)
            .inner_join(item_table).on(sle.item_code == item_table.name)
            .select(
                sle.item_code, sle.warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
                sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference,
                sle.item_code.as_("name"), sle.voucher_no, sle.stock_value, sle.batch_no, sle.serial_no,
                sle.serial_and_batch_bundle, sle.has_serial_no, item_table.item_group,
                item_table.stock_uom, item_table.item_name
            )
            .where((sle.docstatus < 2) & (sle.is_cancelled == 0))
            .orderby(sle.posting_datetime).orderby(sle.creation)
        )

        query = self.apply_inventory_dimensions_filters(query, sle)
        query = self.apply_warehouse_filters(query, sle)
        query = self.apply_items_filters(query, item_table)
        query = self.apply_date_filters(query, sle)

        if self.filters.get("company"):
            query = query.where(sle.company == self.filters.get("company"))

        self.sle_query = query

    def apply_inventory_dimensions_filters(self, query, sle):
        for fieldname in self.inventory_dimensions:
            query = query.select(fieldname)
            if self.filters.get(fieldname):
                query = query.where(sle[fieldname].isin(self.filters.get(fieldname)))
        return query

    def apply_warehouse_filters(self, query, sle):
        warehouse_table = frappe.qb.DocType("Warehouse")
        if self.filters.get("warehouse"):
            query = apply_warehouse_filter(query, sle, self.filters)
        elif (warehouse_type := self.filters.get("warehouse_type")):
            query = query.join(warehouse_table).on(warehouse_table.name == sle.warehouse).where(warehouse_table.warehouse_type == warehouse_type)
        return query

    def apply_items_filters(self, query, item_table):
        if item_group := self.filters.get("item_group"):
            children = get_descendants_of("Item Group", item_group, ignore_permissions=True)
            query = query.where(item_table.item_group.isin([*children, item_group]))

        for field in ["item_code", "brand"]:
            if self.filters.get(field):
                if field == "item_code":
                    query = query.where(item_table.name == self.filters.get(field))
                else:
                    query = query.where(item_table[field] == self.filters.get(field))
        return query

    def apply_date_filters(self, query, sle):
        if not self.filters.get("ignore_closing_balance") and self.start_from:
            query = query.where(sle.posting_date >= self.start_from)
        if self.to_date:
            query = query.where(sle.posting_date <= self.to_date)
        return query

    def get_columns_with_warehouse_balances(self):
        columns = [
            {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
            {"label": _("Item Name"), "fieldname": "item_name", "width": 150},
            {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 150},
            {"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 150},
        ]
        for warehouse in self.warehouses:
            columns.extend([
                {"label": _(f"{warehouse} Bal Qty"), "fieldname": f"{warehouse}_bal_qty", "fieldtype": "Float", "width": 170, "convertible": "qty"},
                {"label": _(f"{warehouse} Bal Value"), "fieldname": f"{warehouse}_bal_val", "fieldtype": "Currency", "width": 170, "options": "currency"}
            ])
        return columns

    def get_opening_vouchers(self):
        opening_vouchers = {"Stock Entry": [], "Stock Reconciliation": []}
        se, sr = frappe.qb.DocType("Stock Entry"), frappe.qb.DocType("Stock Reconciliation")

        vouchers_data = (
            frappe.qb.from_(
                (
                    frappe.qb.from_(se).select(se.name, Coalesce("Stock Entry").as_("voucher_type")).where((se.docstatus == 1) & (se.posting_date <= self.to_date) & (se.is_opening == "Yes"))
                ) + (
                    frappe.qb.from_(sr).select(sr.name, Coalesce("Stock Reconciliation").as_("voucher_type")).where((sr.docstatus == 1) & (sr.posting_date <= self.to_date) & (sr.purpose == "Opening Stock"))
                )
            ).select("voucher_type", "name")
        ).run(as_dict=True)

        for d in vouchers_data:
            opening_vouchers[d.voucher_type].append(d.name)
        return opening_vouchers

    @staticmethod
    @functools.lru_cache()
    def get_inventory_dimension_fields():
        return [dimension.fieldname for dimension in get_inventory_dimensions()]


def filter_items_with_no_transactions(iwb_map, float_precision: float, inventory_dimensions: list | None = None):
    pop_keys = []
    for group_by_key, qty_dict in iwb_map.items():
        no_transactions = True
        for key, val in qty_dict.items():
            if inventory_dimensions and key in inventory_dimensions:
                continue
            if key in ["item_code", "warehouse", "item_name", "item_group", "project", "stock_uom", "company", "opening_fifo_queue", "currency"]:
                continue
            val = flt(val, float_precision)
            qty_dict[key] = val
            if key != "val_rate" and val:
                no_transactions = False
        if no_transactions:
            pop_keys.append(group_by_key)
    for key in pop_keys:
        iwb_map.pop(key)
    return iwb_map