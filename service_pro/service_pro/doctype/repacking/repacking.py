# Copyright (c) 2025, jan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, nowdate, nowtime, flt
from erpnext.stock.utils import get_incoming_rate


class Repacking(Document):

    def calculate_valuation_rates_like_stock_entry(self):
        """
        Calculate valuation rates for repack_item table using the same logic as Stock Entry
        This mimics the set_basic_rate method from Stock Entry
        """
        if not self.repack_item:
            return
            
        # Calculate outgoing items cost (similar to Stock Entry's set_rate_for_outgoing_items)
        outgoing_items_cost = 0.0
        
        for item in self.repack_item:
            if not item.item_code or not item.warehouse:
                continue
                
            # Get incoming rate using the same method as Stock Entry
            args = self.get_args_for_incoming_rate(item)
            rate = get_incoming_rate(args, raise_error_if_no_rate=False)
            
            if rate and rate >= 0:
                item.valuation_rate = rate
                item.basic_amount = flt(item.qty or 0) * flt(rate)
                outgoing_items_cost += flt(item.basic_amount)
            else:
                # Fallback to zero if no rate found
                item.valuation_rate = 0.0
                item.basic_amount = 0.0
        
        # Store outgoing cost for target item calculations
        self.total_outgoing_value = outgoing_items_cost
        
      
    
    def get_args_for_incoming_rate(self, item):
        """
        Get arguments for incoming rate calculation - same as Stock Entry
        """
        return frappe._dict({
            "item_code": item.item_code,
            "warehouse": item.warehouse,
            "posting_date": self.posting_date or nowdate(),
            "posting_time": self.posting_time or nowtime(),
            "qty": -1 * flt(item.qty or 1),  # Negative for outgoing
            "voucher_type": self.doctype,
            "voucher_no": self.name,
            "company": self.company,
            "allow_zero_valuation": 0,
            "batch_no": getattr(item, 'batch_no', None),
            "serial_no": getattr(item, 'serial_no', None),
        })
    
    def calculate_target_item_rates(self, outgoing_items_cost):
        """
        Calculate rates for target items using the same logic as Stock Entry's 
        get_basic_rate_for_repacked_items method
        """
        if not self.target_item:
            return
            
        # Get finished items (target items)
        finished_items = [d.target_item_code or d.item_code for d in self.target_item if d.target_item_code or d.item_code]
        
        if len(set(finished_items)) == 1:
            # Single type of finished item
            total_target_qty = sum([flt(d.qty) for d in self.target_item if d.qty])
            if total_target_qty > 0:
                rate_per_unit = flt(outgoing_items_cost / total_target_qty)
                
                for item in self.target_item:
                    if item.qty:
                        item.valuation_rate = rate_per_unit
                        item.amount = flt(item.qty) * rate_per_unit
        else:
            # Multiple types of finished items - distribute proportionally
            total_target_qty = sum([flt(d.qty) for d in self.target_item if d.qty])
            if total_target_qty > 0:
                for item in self.target_item:
                    if item.qty:
                        # Distribute cost proportionally based on quantity
                        proportion = flt(item.qty) / total_target_qty
                        item.amount = flt(outgoing_items_cost * proportion)
                        item.valuation_rate = flt(item.amount / item.qty) if item.qty else 0
    
    def set_rates_from_stock_entry_logic(self):
        """
        Main method to set rates using Stock Entry logic
        Call this method to update all valuation rates
        """
        try:
            self.calculate_valuation_rates_like_stock_entry()
            self.calculate_total_values()
            
            frappe.msgprint(
                _("Valuation rates updated using Stock Entry calculation logic"),
                title=_("Rates Updated"),
                indicator="green"
            )
            
        except Exception as e:
            frappe.log_error(f"Error calculating rates for Repacking {self.name}: {str(e)}", "Repacking Rate Calculation")
            frappe.throw(_("Error calculating valuation rates: {0}").format(str(e)))

    @frappe.whitelist()
    def update_rates_from_stock_entry_logic(self):
        """
        Whitelist method to be called from frontend
        """
        self.set_rates_from_stock_entry_logic()
        return True

    @frappe.whitelist()
    def generate_items(self):
        """Generate Item documents for all target items that don't have target_item_code"""
        if not self.target_item:
            frappe.throw(_("No target items found to generate"))

        production_settings = frappe.get_single("Production Settings")

        if not production_settings:
            frappe.throw(_("Production Settings not found. Please create Production Settings first."))

        repack_item_group = production_settings.get("repack_item_group")
        tax_template = production_settings.get("default_item_tax_template")
        repack_item_naming_series = production_settings.get("repack_item_naming_series")

        if not repack_item_group:
            frappe.throw(_("Please set the default Item Group in Production Settings"))
        if not repack_item_naming_series:
            frappe.throw(_("Please set the default Item Naming Series in Production Settings"))

        generated_items = []
        errors = []

        for target_item in self.target_item:
            if target_item.target_item_code:
                continue

            if not target_item.item_name:
                errors.append(_("Row {0}: Please add a valid item name").format(target_item.idx))
                continue
            if not target_item.uom:
                errors.append(_("Row {0}: Please add a valid UOM").format(target_item.idx))
                continue

            try:
                item_doc = frappe.new_doc("Item")
                item_doc.update({
                    "item_name": target_item.item_name,
                    "stock_uom": target_item.uom,
                    "item_group": repack_item_group,
                    "naming_series": repack_item_naming_series,
                    "is_stock_item": 1,
                    "include_item_in_manufacturing": 1,
                    "custom_tax_template": tax_template,
                    # Add default valuation rate to prevent zero valuation errors
                    "valuation_rate": target_item.valuation_rate or 0,
                })

                # UPDATED TAX TEMPLATE LOGIC
                if tax_template:
                    tax_details = frappe.get_all(
                        "Item Tax",
                        filters={"parent": tax_template},
                        fields=["item_tax_template", "tax_category"]
                    )
                    for tax in tax_details:
                        item_doc.append("taxes", {
                            "item_tax_template": tax.get("item_tax_template"),
                            "tax_category": tax.get("tax_category"),
                        })

                item_doc.insert(ignore_permissions=True)
                target_item.target_item_code = item_doc.name

                generated_items.append({
                    "row": target_item.idx,
                    "item_name": target_item.item_name,
                    "item_code": item_doc.name,
                    "uom": target_item.uom
                })

            except Exception as e:
                error_msg = _("Row {0} - Error creating item '{1}': {2}").format(
                    target_item.idx, target_item.item_name, str(e)
                )
                errors.append(error_msg)
                frappe.log_error(f"Error creating item for {target_item.item_name}: {str(e)}", "Repacking Item Generation")

        if errors:
            error_message = "<br>".join(errors)
            if generated_items:
                frappe.msgprint(
                    _("Some items were generated successfully, but there were errors:<br><br>{0}").format(error_message),
                    title=_("Partial Success"),
                    indicator="orange"
                )
            else:
                frappe.throw(_("Failed to generate items:<br><br>{0}").format(error_message))

        if generated_items:
            try:
                for item in generated_items:
                    for target_item in self.target_item:
                        if (target_item.item_name == item["item_name"] and
                            target_item.uom == item["uom"] and
                            target_item.idx == item["row"]):
                            frappe.db.set_value(
                                target_item.doctype,
                                target_item.name,
                                "target_item_code",
                                item["item_code"]
                            )
                            break
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(f"Error updating target_item_code fields: {str(e)}", "Repacking Field Update Error")
                frappe.throw(_("Error updating target item codes: {0}").format(str(e)))

            return {
                "success": True,
                "generated_items": generated_items,
                "message": f"Generated {len(generated_items)} items successfully",
                "updated_fields": True
            }
        else:
            if not errors:
                frappe.msgprint(
                    _("No new items to generate. All target items already have item codes."),
                    title=_("No Action Needed"),
                    indicator="blue"
                )
            return {"success": False, "message": "No items generated"}

    @frappe.whitelist()
    def generate_single_item(self, target_item_name, uom, row_name=None, valuation_rate=0):
        production_settings = frappe.get_single("Production Settings")

        if not production_settings:
            frappe.throw(_("Production Settings not found. Please create Production Settings first."))

        repack_item_group = production_settings.get("repack_item_group")
        tax_template = production_settings.get("default_item_tax_template")
        repack_item_naming_series = production_settings.get("repack_item_naming_series")

        if not repack_item_group:
            frappe.throw(_("Please set the default Item Group in Production Settings"))
        if not repack_item_naming_series:
            frappe.throw(_("Please set the default Item Naming Series in Production Settings"))
        if not target_item_name:
            frappe.throw(_("Please add a valid item name"))
        if not uom:
            frappe.throw(_("Please add a valid UOM"))

        try:
            item_doc = frappe.new_doc("Item")
            item_doc.update({
                "item_name": target_item_name,
                "stock_uom": uom,
                "item_group": repack_item_group,
                "naming_series": repack_item_naming_series,
                "is_stock_item": 1,
                "include_item_in_manufacturing": 1,
                "custom_tax_template": tax_template,
                "valuation_rate": flt(valuation_rate) or 0,
            })

            # UPDATED TAX TEMPLATE LOGIC
            if tax_template:
                tax_details = frappe.get_all(
                    "Item Tax",
                    filters={"parent": tax_template},
                    fields=["item_tax_template", "tax_category"]
                )
                for tax in tax_details:
                    item_doc.append("taxes", {
                        "item_tax_template": tax.get("item_tax_template"),
                        "tax_category": tax.get("tax_category"),
                    })

            item_doc.insert(ignore_permissions=True)

            if row_name:
                frappe.db.set_value("Target Item", row_name, "target_item_code", item_doc.name)
                frappe.db.commit()

            frappe.msgprint(
                _("Item '{0}' created successfully with code: {1}").format(
                    target_item_name, item_doc.name
                ),
                title=_("Item Created"),
                indicator="green"
            )

            return {
                "success": True,
                "item_code": item_doc.name,
                "item_name": target_item_name
            }

        except Exception as e:
            error_msg = _("Error creating item '{0}': {1}").format(target_item_name, str(e))
            frappe.log_error(f"Error creating single item {target_item_name}: {str(e)}", "Repacking Single Item Generation")
            frappe.throw(error_msg)

    def calculate_total_values(self):
        """Calculate total outgoing, incoming, and difference values"""
        total_outgoing = 0
        total_incoming = 0
        
        # Calculate total outgoing value from repack_item table
        if self.repack_item:
            for item in self.repack_item:
                if item.valuation_rate and item.qty:
                    total_outgoing += flt(item.valuation_rate) * flt(item.qty)
                elif item.valuation_rate and not item.qty:
                    total_outgoing += flt(item.valuation_rate)
        
        # Calculate total incoming value from target_item table using amount field
        if self.target_item:
            for item in self.target_item:
                if hasattr(item, 'amount') and item.amount:
                    total_incoming += flt(item.amount)
                elif item.valuation_rate and item.qty:
                    total_incoming += flt(item.valuation_rate) * flt(item.qty)
                elif item.valuation_rate and not item.qty:
                    total_incoming += flt(item.valuation_rate)
        
        # Calculate difference (outgoing - incoming)
        total_difference = total_outgoing - total_incoming
        
        # Set the calculated values
        self.total_outgoing_value = total_outgoing
        self.total_incoming_value = total_incoming
        self.total_difference_value = total_difference
        
        return {
            "total_outgoing": total_outgoing,
            "total_incoming": total_incoming,
            "total_difference": total_difference
        }

    def fix_stock_entry_amounts(self, stock_entry_name):
        """Fix amounts in stock entry after creation"""
        try:
            stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
            
            # Map target items to stock entry items
            source_items_count = len(self.repack_item)
            
            for i, target_item in enumerate(self.target_item):
                target_amount = flt(target_item.amount or 0)
                if target_amount > 0:
                    se_item_index = source_items_count + i
                    if se_item_index < len(stock_entry.items):
                        se_item = stock_entry.items[se_item_index]
                        
                        # Update the amount, basic_amount, and basic_rate directly in database
                        frappe.db.set_value(
                            "Stock Entry Detail", 
                            se_item.name, 
                            {
                                "amount": target_amount,
                                "basic_amount": target_amount,  # Set basic_amount same as amount
                                "basic_rate": target_amount / flt(target_item.qty) if target_item.qty else 0
                            }
                        )
            
            frappe.db.commit()
            
        except Exception as e:
            frappe.log_error(f"Error fixing stock entry amounts: {str(e)}", "Repacking Amount Fix")

    def create_stock_entry(self):
        try:
            if not self.company:
                frappe.throw(_("Company is required to create Stock Entry"))

            if not self.repack_item or len(self.repack_item) == 0:
                frappe.throw(_("Source items (Repack Item table) are required"))

            if not self.target_item or len(self.target_item) == 0:
                frappe.throw(_("Target items are required"))

            stock_entry = frappe.new_doc("Stock Entry")
            stock_entry.update({
                "stock_entry_type": "Repack",
                "company": self.company,
                "posting_date": self.posting_date or nowdate(),
                "posting_time": self.posting_time or nowtime(),
                "set_posting_time": 1,
                "purpose": "Repack",
                "reference_doctype": self.doctype,
                "reference_docname": self.name,
                "custom_repacking_no": self.name,
            })

            # Add source items (outgoing) - USE MANUAL VALUATION RATES
            for repack_item in self.repack_item:
                if not repack_item.item_code:
                    frappe.throw(_("Item Code is required in Repack Item table, Row {0}").format(repack_item.idx))
                if not repack_item.warehouse:
                    frappe.throw(_("Warehouse is required in Repack Item table, Row {0}").format(repack_item.idx))
                if not repack_item.qty or repack_item.qty <= 0:
                    frappe.throw(_("Quantity must be greater than 0 in Repack Item table, Row {0}").format(repack_item.idx))

                # Use the manually entered valuation rate (which can be from incoming rate)
                manual_rate = flt(repack_item.valuation_rate or 0)

                # Create stock entry item
                se_item = {
                    "item_code": repack_item.item_code,
                    "s_warehouse": repack_item.warehouse,
                    "qty": repack_item.qty,
                    "basic_rate": manual_rate,  # Use manually entered rate (can be from incoming rate)
                    "uom": repack_item.uom,
                    "cost_center": self.cost_center,
                    "conversion_factor": 1,
                }

                # FIXED: Handle batch using Serial and Batch Bundle instead of direct batch_no
                if hasattr(repack_item, 'batch_no') and repack_item.batch_no:
                    # Check if item uses batch tracking
                    item_doc = frappe.get_doc("Item", repack_item.item_code)
                    if item_doc.has_batch_no:
                        # Create Serial and Batch Bundle for source item
                        bundle_doc = frappe.new_doc("Serial and Batch Bundle")
                        bundle_doc.update({
                            "item_code": repack_item.item_code,
                            "warehouse": repack_item.warehouse,
                            "type_of_transaction": "Outward",
                            "voucher_type": "Stock Entry",
                            "company": self.company,
                            "posting_date": self.posting_date or nowdate(),
                            "posting_time": self.posting_time or nowtime(),
                        })
                        
                        # Add batch entry
                        bundle_doc.append("entries", {
                            "batch_no": repack_item.batch_no,
                            "qty": repack_item.qty,
                            "warehouse": repack_item.warehouse
                        })
                        
                        bundle_doc.insert(ignore_permissions=True)
                        se_item["serial_and_batch_bundle"] = bundle_doc.name

                stock_entry.append("items", se_item)

            # Add target items (incoming)
            for target_item in self.target_item:
                item_code = target_item.target_item_code or target_item.item_code

                if not item_code:
                    frappe.throw(_("Item Code or Target Item Code is required in Target Item table, Row {0}").format(target_item.idx))
                if not target_item.warehouse:
                    frappe.throw(_("Warehouse is required in Target Item table, Row {0}").format(target_item.idx))
                if not target_item.qty or target_item.qty <= 0:
                    frappe.throw(_("Quantity must be greater than 0 in Target Item table, Row {0}").format(target_item.idx))

                # Calculate valuation rate based on amount if available
                calculated_rate = 0
                target_amount = flt(target_item.amount or 0)
                target_qty = flt(target_item.qty or 0)
                
                if target_amount > 0 and target_qty > 0:
                    calculated_rate = target_amount / target_qty
                else:
                    calculated_rate = flt(target_item.valuation_rate or 0)
                
                # Check if zero valuation is allowed
                allow_zero_rate = False
                if calculated_rate == 0:
                    # Check if this is a newly created item without stock transactions
                    item_doc = frappe.get_doc("Item", item_code)
                    if item_doc.creation >= self.creation:  # Recently created item
                        allow_zero_rate = True
                        # Calculate rate based on total outgoing value distributed across target quantities
                        if self.total_outgoing_value and self.target_item:
                            total_target_qty = sum([flt(ti.qty) for ti in self.target_item if ti.qty])
                            if total_target_qty > 0:
                                calculated_rate = flt(self.total_outgoing_value) / total_target_qty
                                target_amount = calculated_rate * target_qty

                # Create stock entry item
                se_item = {
                    "item_code": item_code,
                    "t_warehouse": target_item.warehouse,
                    "qty": target_qty,
                    "uom": target_item.uom,
                    "cost_center": self.cost_center,
                    "conversion_factor": 1,
                    "allow_zero_valuation_rate": allow_zero_rate,
                    "set_basic_rate_manually": 1,
                }
                
                # Set amount, basic_amount, and basic_rate with the calculated rate
                if target_amount > 0:
                    se_item["amount"] = target_amount
                    se_item["basic_amount"] = target_amount  # Set basic_amount same as amount
                    se_item["basic_rate"] = calculated_rate  # Use calculated rate
                else:
                    se_item["basic_rate"] = calculated_rate  # Use calculated rate
                    # If no amount specified, calculate based on rate
                    if calculated_rate > 0:
                        calculated_amount = calculated_rate * target_qty
                        se_item["amount"] = calculated_amount
                        se_item["basic_amount"] = calculated_amount  # Set basic_amount same as amount

                # FIXED: Handle batch for target items using Serial and Batch Bundle
                if hasattr(target_item, 'batch_no') and target_item.batch_no:
                    # Check if item uses batch tracking
                    item_doc = frappe.get_doc("Item", item_code)
                    if item_doc.has_batch_no:
                        # Create Serial and Batch Bundle for target item
                        bundle_doc = frappe.new_doc("Serial and Batch Bundle")
                        bundle_doc.update({
                            "item_code": item_code,
                            "warehouse": target_item.warehouse,
                            "type_of_transaction": "Inward",
                            "voucher_type": "Stock Entry",
                            "company": self.company,
                            "posting_date": self.posting_date or nowdate(),
                            "posting_time": self.posting_time or nowtime(),
                        })
                        
                        # Add batch entry
                        bundle_doc.append("entries", {
                            "batch_no": target_item.batch_no,
                            "qty": target_qty,
                            "warehouse": target_item.warehouse
                        })
                        
                        bundle_doc.insert(ignore_permissions=True)
                        se_item["serial_and_batch_bundle"] = bundle_doc.name

                stock_entry.append("items", se_item)

            # Insert stock entry
            stock_entry.insert(ignore_permissions=True)
            
            # Important: Set amount and basic_amount again after insert to ensure they're preserved
            for i, target_item in enumerate(self.target_item):
                target_amount = flt(target_item.amount or 0)
                if target_amount > 0:
                    # Find the corresponding stock entry item (source items come first)
                    se_item_index = len(self.repack_item) + i
                    if se_item_index < len(stock_entry.items):
                        stock_entry.items[se_item_index].amount = target_amount
                        stock_entry.items[se_item_index].basic_amount = target_amount  # Set basic_amount same as amount
                        stock_entry.items[se_item_index].basic_rate = target_amount / flt(target_item.qty) if target_item.qty else 0
            
            try:
                stock_entry.run_method("set_missing_values")
                stock_entry.save()
                
                # Then calculate and submit
                stock_entry.calculate_rate_and_amount()
                stock_entry.save()
                stock_entry.submit()
                
                # Fix amounts after submission if needed
                self.fix_stock_entry_amounts(stock_entry.name)
                
            except Exception as calc_error:
                # If there's still a valuation error, try with zero valuation allowed
                if "Valuation Rate" in str(calc_error) and "is required" in str(calc_error):
                    frappe.msgprint(
                        _("Enabling zero valuation rate for newly created items and retrying..."),
                        title=_("Adjusting Valuation"),
                        indicator="orange"
                    )
                    
                    # Enable allow_zero_valuation_rate for all target items
                    for item in stock_entry.items:
                        if item.t_warehouse:  # Target items
                            item.allow_zero_valuation_rate = 1
                    
                    stock_entry.save()
                    stock_entry.submit()
                    
                    # Fix amounts after submission
                    self.fix_stock_entry_amounts(stock_entry.name)
                else:
                    raise calc_error

            # Update the reference in repacking document
            if hasattr(self, 'stock_entry'):
                self.db_set("stock_entry", stock_entry.name)

            frappe.msgprint(
                _("Stock Entry {0} created successfully").format(stock_entry.name),
                title=_("Stock Entry Created"),
                indicator="green"
            )

            return stock_entry.name

        except Exception as e:
            frappe.log_error(f"Error creating Stock Entry for Repacking {self.name}: {str(e)}", "Repacking Stock Entry Creation")
            frappe.throw(_("Error creating Stock Entry: {0}").format(str(e)))

    def on_cancel(self):
        if hasattr(self, 'stock_entry') and self.stock_entry:
            try:
                stock_entry_doc = frappe.get_doc("Stock Entry", self.stock_entry)
                if stock_entry_doc.docstatus == 1:
                    stock_entry_doc.cancel()
                    frappe.msgprint(
                        _("Related Stock Entry {0} has been cancelled").format(self.stock_entry),
                        title=_("Stock Entry Cancelled"),
                        indicator="orange"
                    )
            except Exception as e:
                frappe.log_error(f"Error cancelling Stock Entry {self.stock_entry}: {str(e)}", "Repacking Stock Entry Cancellation")
                frappe.msgprint(
                    _("Error cancelling related Stock Entry {0}: {1}").format(self.stock_entry, str(e)),
                    title=_("Stock Entry Cancellation Error"),
                    indicator="red"
                )
        else:
            try:
                stock_entries = frappe.get_all("Stock Entry", 
                    filters={
                        "reference_doctype": self.doctype,
                        "reference_docname": self.name,
                        "docstatus": 1
                    }
                )
                for se in stock_entries:
                    stock_entry_doc = frappe.get_doc("Stock Entry", se.name)
                    stock_entry_doc.cancel()
                    frappe.msgprint(
                        _("Related Stock Entry {0} has been cancelled").format(se.name),
                        title=_("Stock Entry Cancelled"),
                        indicator="orange"
                    )
            except Exception as e:
                frappe.log_error(f"Error finding/cancelling Stock Entry for {self.name}: {str(e)}", "Repacking Stock Entry Cancellation")
                frappe.msgprint(
                    _("Error cancelling related Stock Entry: {0}").format(str(e)),
                    title=_("Stock Entry Cancellation Error"),
                    indicator="red"
                )

    def validate(self):
        self.posting_time = nowtime()
        # Calculate amount for each target item
        if self.target_item:
            for item in self.target_item:
                if hasattr(item, 'qty') and hasattr(item, 'valuation_rate'):
                    item.amount = flt(item.qty or 0) * flt(item.valuation_rate or 0)

        # Calculate totals before validation
        self.calculate_total_values()
        self.calculate_valuation_rates_like_stock_entry()
        
        # Validate target items structure
        if self.target_item:
            for item in self.target_item:
                if item.item_name and not item.uom:
                    frappe.throw(_("Row {0}: UOM is required when Item Name is specified").format(item.idx))
                if item.uom and not item.item_name:
                    frappe.throw(_("Row {0}: Item Name is required when UOM is specified").format(item.idx))

        # Validate that required tables have data when submitting
        if self.docstatus == 1:
            if not self.repack_item or len(self.repack_item) == 0:
                frappe.throw(_("At least one source item is required in Repack Item table"))
            if not self.target_item or len(self.target_item) == 0:
                frappe.throw(_("At least one target item is required in Target Item table"))
            
            # Validate total difference value - allow small differences for newly created items
            tolerance = 0.01  # Allow up to 1 unit difference for new items
            if self.total_difference_value and abs(flt(self.total_difference_value)) > tolerance:
                frappe.throw(_("The Total Values have Difference of {0}. Please ensure the outgoing and incoming values are balanced before submitting.").format(
                    flt(self.total_difference_value, 2)
                ))

    def before_save(self):
        if not self.posting_date:
            self.posting_date = nowdate()
        if not self.posting_time:
            self.posting_time = nowtime()
        
        # Calculate amount for each target item before saving
        if self.target_item:
            for item in self.target_item:
                if hasattr(item, 'qty') and hasattr(item, 'valuation_rate'):
                    item.amount = flt(item.qty or 0) * flt(item.valuation_rate or 0)
        
        # Always calculate totals before saving
        self.calculate_total_values()

    def on_submit(self):
        self.create_stock_entry()
    
    def validate_stock_availability(self):
        """Validate stock availability before creating stock entry"""
        insufficient_stock = []
        
        for repack_item in self.repack_item:
            if not repack_item.item_code or not repack_item.warehouse:
                continue
                
            # Get actual stock from Bin
            bin_data = frappe.db.get_value(
                "Bin",
                filters={
                    "item_code": repack_item.item_code,
                    "warehouse": repack_item.warehouse
                },
                fieldname=["actual_qty", "reserved_qty"],
                as_dict=True
            )
            
            available_qty = 0
            if bin_data:
                available_qty = flt(bin_data.actual_qty or 0) - flt(bin_data.reserved_qty or 0)
            
            required_qty = flt(repack_item.qty or 0)
            
            if available_qty < required_qty:
                insufficient_stock.append({
                    "item_code": repack_item.item_code,
                    "warehouse": repack_item.warehouse,
                    "required": required_qty,
                    "available": available_qty,
                    "shortage": required_qty - available_qty
                })
        
        if insufficient_stock:
            error_msg = _("Insufficient stock for the following items:\n")
            for item in insufficient_stock:
                error_msg += _("• {0} in {1}: Need {2}, Available {3} (Short by {4})\n").format(
                    item["item_code"],
                    item["warehouse"], 
                    item["required"],
                    item["available"],
                    item["shortage"]
                )
            frappe.throw(error_msg, title=_("Insufficient Stock"))