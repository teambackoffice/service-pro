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
        if(frm.doc.item_group){
            frappe.db.get_value("Item Group", frm.doc.item_group, 'naming_series_for_item').then(data=>{
                frm.set_value("naming_series", data.message.naming_series_for_item)
            })
        }
    },
    custom_brand_name:function(frm){
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
            }if(frm.doc.custom_brand_name){
                if(frm.doc.item_name){
                    frm.set_value('item_name', frm.doc.item_name + ` ${frm.doc.custom_brand_name}`)
                }else{
                    frm.set_value('item_name', `${frm.doc.custom_brand_name}`)
                }
            }if(frm.doc.custom_item_specification){
                if(frm.doc.item_name){
                    frm.set_value('item_name', frm.doc.item_name + ` ${frm.doc.custom_item_specification}`)
                }else{
                    frm.doc.item_name = ""
                    frm.set_value('item_name', `${frm.doc.custom_item_specification}`)
                }
            }if(frm.doc.custom_size_specification){
                if(frm.doc.item_name){
                    frm.set_value('item_name', frm.doc.item_name + ` ${frm.doc.custom_size_specification}`)
                }else{
                    frm.doc.item_name = ""
                    frm.set_value('item_name', `${frm.doc.custom_size_specification}`)
                    
                }
            }if(frm.doc.custom_item_description){
                if(frm.doc.item_name){
                    frm.set_value('item_name', frm.doc.item_name + ` ${frm.doc.custom_item_description}`)
                }else{
                    frm.doc.item_name = ""
                    frm.set_value('item_name', `${frm.doc.custom_item_description}`)
                }
            }
        }
    },
    before_save:function(frm){
        frm.set_value("custom_edit_naming_fields", false)
        frm.trigger('makeItemname')
    }
})