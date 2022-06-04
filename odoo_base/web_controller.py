import json

import requests

from odoo import http
from odoo.http import request


class Website(http.Controller):
    @http.route(['/auth/get_user_id'], type='http')
    def get_user_id(self):
        user_id = request.uid or 'none'
        return str(user_id)

    @http.route(['/purge/cache'], type='http')
    def purge_cache(self):
        res = {'status': 'error', 'message': 'Nothing'}
        try:
            url_to_purge = request.httprequest.values.get('url')
            url_to_purge = 'http://voiceofnews.com/blog'
            if not url_to_purge:
                return 'Invalid Url'
            token = 'hbWBy99DnEsV7ItOJMh40ssg6Ka_IOCZiEDCNMV-'
            authorization = 'Bearer '+token
            headers = {
                'Authorization': authorization,
                'Content-Type': 'application/json'
            }
            api_url = 'https://api.cloudflare.com/client/v4/zones/ae6d65e2cd285e9f741a60f301a4bfe8/purge_cache'
            urls_to_purge = [
                {'url': url_to_purge}
            ]
            json_data = {'files': urls_to_purge}
            if url_to_purge == 'all':
                json_data = {'purge_everything': True}
            res = requests.post(api_url, headers=headers, json=json_data)
            status = res.status_code
            if status != 200:
                res = res.json()
            else:
                res = {'status': 'success', 'urls': urls_to_purge }
        except Exception as e:
            res['message'] = 'Error in purge => ' + str(e)
        res = json.dumps(res)
        return res

