# -*- coding: utf-8 -*-
from odoo import models, api, fields


class Listing(models.Model):
    _name = 'api.listing'
    title = fields.Char()
    price = fields.Integer()
    categoryId = fields.Integer()
    description = fields.Char()
