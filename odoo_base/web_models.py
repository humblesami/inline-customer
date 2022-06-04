from odoo import http, models
from odoo.addons.base.models.ir_qweb import IrQWeb
from odoo.addons.base.models.qweb import QWeb
from odoo.http import request


class CustomIrQWeb(IrQWeb):
    """ Base QWeb rendering engine
    * to customize ``t-field`` rendering, subclass ``ir.qweb.field`` and
      create new models called :samp:`ir.qweb.field.{widget}`
    Beware that if you need extensions or alterations which could be
    incompatible with other subsystems, you should create a local object
    inheriting from ``ir.qweb`` and customize that.
    """

    _inherit = 'ir.qweb'
    
    def _generate_asset_nodes(self, bundle, css=True, js=True, debug=False, async_load=False, defer_load=False, lazy_load=False, media=None):
        res = super()._generate_asset_nodes(bundle, css, js, debug, async_load, defer_load, lazy_load, media)
        if css:
            res[0][1]['rel'] = "preload"
            res[0][1]['as'] = "style"
            res[0][1]['onload'] = "this.rel='stylesheet'"
        return res