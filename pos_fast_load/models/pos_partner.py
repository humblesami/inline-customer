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
        customer_count = len(res)
        if last_field != 'loading_data_offline':
            if last_field == 'loading_data_offline':
                del fields[-1]
            res = super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            return res
        cr = self._cr
        query = """
                SELECT distinct rp.name as name,rp.id,rp.mobile,rp.barcode,
                rp.street,rp.zip,rp.city,rp.country_id, rp.state_id,rp.temp_id,
                rp.email, rp.vat, rp.write_date,
                rp.mobile as phone                
                from public.res_partner rp
                where customer=true
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
        self.get_related_parents(partners_dict, partner_ids, 'property_account_position_id')

        res = partners
        return res

    def get_related_parents(self, partners_dict, partner_ids, field_name):
        records = self.env['res.partner'].search_read([('id', 'in', partner_ids), (field_name, '!=', False)], fields=[field_name])
        for ob in records:
            partners_dict[ob['id']][field_name] = [ob[field_name][0], ob[field_name][1]]

    @api.model_create_multi
    def create(self, vals_list):
        for ob in vals_list:
            ob['customer'] = True
            if ob.get('mobile'):
                if not ob.get('phone'):
                    ob['phone'] = ob['mobile']
            if ob.get('phone'):
                if not ob.get('mobile'):
                    ob['mobile'] = ob['phone']
        res = super().create(vals_list)
        for ob in res:
            if ob.mobile:
                if self.search_count([('mobile', '=', ob.mobile)]) > 1 or self.search_count([('mobile', '=', ob.phone)]) > 1:
                    raise ValidationError('Mobile No Already Exists')
        return res

    def write(self, vals):
        phone_number = False
        mobile_number = False
        if vals.get('phone'):
            phone_number = vals.get('phone')
        if vals.get('mobile'):
            mobile_number = vals.get('mobile')
        if phone_number and not mobile_number:
            if not self.mobile:
                vals['mobile'] = phone_number
        if mobile_number and not phone_number:
            if not self.phone:
                vals['phone'] = mobile_number
        res = super(ResPartnerTSTInherit, self).write(vals)
        return res