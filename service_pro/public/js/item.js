frappe.ui.form.on('Item', {
    refresh:function(frm){
        if(frm.doc.is_stock_item){
            frm.set_df_property("item_name","read_only",1)
        }
    },
    is_stock_item:function(frm){
        frm.set_df_property("item_name","read_only",frm.doc.is_stock_item)
    },
    item_group:function(frm){
        frm.trigger('makeItemname')
    },
    brand:function(frm){
        frm.trigger('makeItemname')
    },
    custom_item_specification:function(frm){
        frm.trigger('makeItemname')
    },
    custom_size_specification:function(frm){
        frm.trigger('makeItemname')
    },
    custom_item_description:function(frm){
        frm.trigger('makeItemname')
    },
    makeItemname:function(frm){
        if(frm.doc.is_stock_item){
            if(frm.doc.item_group){
                frm.set_value('item_name', `${frm.doc.item_group}`)
            }
            if(frm.doc.brand){
                frm.set_value('item_name', frm.doc.item_name + ` ${frm.doc.brand}`)
            }if(frm.doc.custom_item_specification){
                frm.set_value('item_name', frm.doc.item_name + ` ${frm.doc.custom_item_specification}`)
            }if(frm.doc.custom_size_specification){
                frm.set_value('item_name', frm.doc.item_name + ` ${frm.doc.custom_size_specification}`)
            }if(frm.doc.custom_item_description){
                frm.set_value('item_name', frm.doc.item_name + ` ${frm.doc.custom_item_description}`)
            }
        }
    },
    before_save:function(frm){
        frm.trigger('makeItemname')
    }
})