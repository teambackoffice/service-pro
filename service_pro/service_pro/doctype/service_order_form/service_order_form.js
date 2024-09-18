// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Service Order Form", {
// 	refresh(frm) {

// 	},
// });
// Event listeners for child table fields (qty, rate, discount, discount_percentage)
// Event listeners for child table fields (qty, rate, discount, discount_percentage)
frappe.ui.form.on('Service Order Form Item', {
    qty: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        calculate_total(frm);
    },
    rate: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        calculate_total(frm);
    },
    discount: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        calculate_total(frm);
    },
    discount_percentage: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
        calculate_total(frm);
    }
});

// Function to calculate the amount for each row in the child table
function calculate_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];  // Get the child table row

    let qty = row.qty || 0;
    let rate = row.rate || 0;
    let discount = row.discount || 0;
    let discount_percentage = row.discount_percentage || 0;

    let amount = qty * rate;

    // Apply discount based on the discount percentage if provided
    if (discount_percentage > 0) {
        let discountAmountPercentage = (amount * discount_percentage) / 100;
        
        // Set the calculated discount amount in the discount field
        frappe.model.set_value(cdt, cdn, 'discount', discountAmountPercentage);
        
        amount -= discountAmountPercentage;
    } else {
        // If discount percentage is not provided, use the fixed discount amount
        amount -= discount;
    }

    // Ensure amount does not go below zero
    amount = Math.max(amount, 0);

    // Set the calculated amount in the current row
    frappe.model.set_value(cdt, cdn, 'amount', amount);

    // Refresh the child table field
    frm.refresh_field('option1');  // Replace 'option1' with your actual child table field name
}

// Event listeners for the main form and child table row add/remove events
frappe.ui.form.on('Service Order Form', {
    refresh: function(frm) {
        calculate_total(frm);
    },

    option1_add: function(frm, cdt, cdn) {
        calculate_total(frm);
    },

    option1_remove: function(frm, cdt, cdn) {
        calculate_total(frm);
    },

    additional_discount_percentage: function(frm) {
        calculate_total(frm);
    },

    apply_additional_discount_on: function(frm) {
        calculate_total(frm);
    },
    
    // Trigger when the tax_amount field is changed
    tax_amount: function(frm) {
        calculate_total(frm);
    },
});

// Function to calculate the total amount from all the rows in the child table and include tax
function calculate_total(frm) {
    let total = 0;

    // Loop through the child table rows and sum the amount fields
    frm.doc.option1.forEach(function(row) {
        total += row.amount || 0;
    });

    // Set the total (without additional discount) in the 'total' field
    frm.set_value('total', total);

    // Get the additional discount percentage
    let additional_discount_percentage = frm.doc.additional_discount_percentage || 0;

    // Initialize variables for additional discount amount and net/grand total
    let additional_discount_amount = 0;
    let net_total = total;
    let grand_total = total;

    // Check the value of apply_additional_discount_on field
    if (frm.doc.apply_additional_discount_on === 'Net Total') {
        // If discount is applied on Net Total, reduce it from net_total
        if (additional_discount_percentage > 0) {
            additional_discount_amount = (total * additional_discount_percentage) / 100;
            net_total -= additional_discount_amount;
        }

        // Ensure the net_total does not go below zero
        net_total = Math.max(net_total, 0);

        frm.set_value('net_total', net_total);
        grand_total = net_total;  // Set the grand total to be the same as the net total for now
    } else if (frm.doc.apply_additional_discount_on === 'Grand Total') {
        // If discount is applied on Grand Total, reduce it from grand_total
        if (additional_discount_percentage > 0) {
            additional_discount_amount = (total * additional_discount_percentage) / 100;
            grand_total -= additional_discount_amount;
        }

        // Ensure the grand_total does not go below zero
        grand_total = Math.max(grand_total, 0);

        frm.set_value('net_total', total);  // Net total will remain unchanged
    }

    // Set the additional discount amount in the 'additional_discount_amount' field
    frm.set_value('additional_discount_amount', additional_discount_amount);

    // Add the tax amount to the grand total
    let tax_amount = frm.doc.tax_amount || 0;
    grand_total += tax_amount;

    // Ensure the grand_total does not go below zero after applying the tax
    grand_total = Math.max(grand_total, 0);

    // Set the calculated grand total
    frm.set_value('grand_total', grand_total);
}
