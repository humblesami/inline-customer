from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartnerTSTInherit(models.Model):
    _inherit = 'res.partner'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if not domain:
            domain = []
        res = super()._search(domain, offset, limit, order)
        last_field = fields[len(fields) - 1]
        if last_field != 'loading_data_offline':
            if last_field == 'loading_data_offline':
                del fields[-1]
            res = super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            return res
        cr = self._cr
        # rp.property_product_pricelist, rp.barcode
        # where customer=true
        query = """
                SELECT distinct 
                rp.id, rp.name, rp.street, rp.city, rp.state_id, rp.country_id, rp.vat, rp.lang
                , rp.phone, rp.zip, rp.mobile, rp.email, rp.write_date                
                from public.res_partner rp                
        """
        cr.execute(query)
        partners = cr.dictfetchall()
        partner_ids = []
        partners_dict = {}
        for customer in partners:
            for key in customer:
                if not customer.get(key):
                    customer[key] = False
            customer['write_date'] = str(customer['write_date'])[0:19]
            partner_ids.append(customer['id'])
            partners_dict[customer['id']] = customer

        self.get_related_parents(partners_dict, partner_ids, 'country_id')
        self.get_related_parents(partners_dict, partner_ids, 'state_id')
        # self.get_related_parents(partners_dict, partner_ids, 'property_account_position_id')

        res = partners
        return res

    def get_related_parents(self, partners_dict, partner_ids, field_name):
        records = self.env['res.partner'].search_read([('id', 'in', partner_ids), (field_name, '!=', False)], fields=[field_name])
        for ob in records:
            partners_dict[ob['id']][field_name] = [ob[field_name][0], ob[field_name][1]]
