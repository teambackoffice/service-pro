import frappe
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import unique
@frappe.whitelist()
def get_sales_person(doctype, txt, searchfield, start, page_len, filters):
    conditions = []
    sales_persons = frappe.db.sql(""" SELECT SP.name as name from `tabSales Person` AS SP 
                  INNER JOIN `tabSales Team` AS ST ON ST.sales_person = SP.name
                   INNER JOIN `tabSales Invoice` AS SI ON SI.name = ST.parent and SI.docstatus = 1 and SI.agent_commision_record = 0
                  WHERE SP.enabled = 1 """,
                                  as_dict=1)
    sales_persons_has_si = []
    for i in sales_persons:
        if i.name not in sales_persons_has_si:
            sales_persons_has_si.append(i.name)

    return frappe.db.sql("""select SP.name from `tabSales Person` AS SP
    		where SP.enabled = 1
    		    and SP.name like %(txt)s
    		    and SP.name in {names}
    			{fcond} {mcond}
    		order by
    			if(locate(%(_txt)s, SP.name), locate(%(_txt)s, SP.name), 99999),
    			SP.idx desc,
    			SP.name
    		limit %(start)s, %(page_len)s""".format(**{
        'fcond': get_filters_cond(doctype, filters, conditions),
        'names': tuple(sales_persons_has_si),
        'mcond': get_match_cond(doctype)
    }), {
        'txt': "%%%s%%" % txt,
        '_txt': txt.replace("%", ""),
        'start': start,
        'page_len': page_len
    })


def get_fields(doctype, fields=[]):
    meta = frappe.get_meta(doctype)
    fields.extend(meta.get_search_fields())

    if meta.title_field and not meta.title_field.strip() in fields:
        fields.insert(1, meta.title_field.strip())

    return unique(fields)