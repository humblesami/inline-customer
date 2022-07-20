import json

from odoo import http
from odoo.http import request


class ApiController(http.Controller):

    @http.route('/api/user-update', type="http", csrf=False, cors='*', auth="public")
    def api_user_update(self, **kw):
        res = {'status': 'error', 'data': 'Unknown'}
        try:
            model_obj = request.env['res.users']
            kw['login'] = kw.get('email') or ''
            kw['phone'] = kw.get('mobile') or ''
            fields = ['name', 'email', 'mobile', 'login', 'phone']
            missing_fields = []
            for field in fields:
                if not kw.get(field):
                    missing_fields.append(field)
            if len(missing_fields):
                res['data'] = 'Missing Fields => ' + (','.join(missing_fields))
            else:
                if kw.get('id'):
                    item = model_obj.sudo().search([('id', '=', kw['id'])])
                    item.write(kw)
                    res['data'] = kw
                else:
                    new_user = model_obj.sudo().create(kw)
                    user_data = kw
                    user_data['id'] = new_user.id
                    res['data'] = user_data
                res['status'] = 'success'
        except Exception as e:
            res['status'] = 'error'
            res['data'] = str(e)
        try:
            request._cr.commit()
        except Exception as e:
            request._cr.rollback()
            if res.get('status') != 'error':
                res['status'] = 'error'
                res['data'] = str(e)
        print(res)
        res = json.dumps(res)
        return res

    @http.route('/api/user-list', type="http", csrf=False, cors='*', auth="public")
    def api_user_list(self, **kw):
        res = {'status': 'error', 'data': 'Unknown'}
        try:
            model_obj = request.env['res.users']
            fields = ['id', 'name', 'email', 'mobile']
            objects_list = model_obj.sudo().search_read(fields=fields)
            res['status'] = 'success'
            res['data'] = objects_list
            # return res
        except Exception as e:
            res['data'] = str(e)
        res = json.dumps(res)
        return res

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
                    if kw.get('id'):
                        item = model_obj.search([('id', '=', kw['id'])])
                        item.write(kw)
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