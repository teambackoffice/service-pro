// Copyright (c) 2024, jan and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Service Order Form", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Service Order Form Item', {
    qty: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    },
    rate: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn); 
    },
    discount: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    },
    discount_percentage: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    }
});

function calculate_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];  // Get the child table row

    // Ensure that qty, rate, discount, and discount_percentage are numbers
    let qty = row.qty || 0;
    let rate = row.rate || 0;
    let discount = row.discount || 0;
    let discount_percentage = row.discount_percentage || 0;

    // Calculate the initial amount (qty * rate)
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

    amount = Math.max(amount, 0);
    
    // Set the amount in the current row
    frappe.model.set_value(cdt, cdn, 'amount', amount);

    // Refresh the child table field
    frm.refresh_field('option1');  // Replace 'option1' with the actual name of your child table field
}

