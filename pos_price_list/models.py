# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    is_takeaway = fields.Boolean('Is Takeaway POS?')
    effective_amount = fields.Float()
    applied_pricelist = fields.Many2one('product.pricelist')