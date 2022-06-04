from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    special_price_list = fields.Many2one('product.pricelist')