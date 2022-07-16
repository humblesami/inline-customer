import json

from odoo import http
from odoo.http import request


class ApiController(http.Controller):

    @http.route('/api/listings', type="http", csrf=False, cors='*', auth="public")
    def api_listing(self, **kw):
        res = {'status': 'error', 'data': 'Unknown'}
        try:
            method = request.httprequest.method
            model_obj = request.env['api.listing']
            fields = ['title', 'price', 'description', 'categoryId']
            if method == 'POST':
                missing_fields = []
                for field in fields:
                    if not kw.get(field):
                        missing_fields.append(field)
                if len(missing_fields):
                    res['data'] = 'Missing Fields => ' + (','.join(missing_fields))
                else:
                    model_obj.create(kw)
                    res = {'status': 'success'}
            else:
                objects_list = model_obj.search_read(fields=fields)
                res['status'] = 'success'
                res['data'] = objects_list
        except Exception as e:
            res['data'] = str(e)
        res = json.dumps(res)
        return res
