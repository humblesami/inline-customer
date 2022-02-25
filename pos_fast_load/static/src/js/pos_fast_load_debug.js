odoo.define('pos_fast_load',function(require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var Model = require('web.rpc');
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var session = require('web.session');
    models.PosModel = models.PosModel.extend({
        //load all data offline efficiently
        //just added 'loading_data_offline' field which changes the search_read method
        load_server_data: function(){
            var self = this;
            var progress = 0;
            var progress_step = 1.0 / self.models.length;
            var tmp = {}; // this is used to share a temporary state between models loaders

            var loaded = new Promise(function (resolve, reject) {
                function load_model(index) {
                    if (index >= self.models.length) {
                        resolve();
                    } else {
                        var model = self.models[index];
                        self.chrome.loading_message(_t('Loading')+' '+(model.label || model.model || ''), progress);

                        var cond = typeof model.condition === 'function'  ? model.condition(self,tmp) : true;
                        if (!cond) {
                            load_model(index+1);
                            return;
                        }

                        var fields =  typeof model.fields === 'function'  ? model.fields(self,tmp)  : model.fields;
                        var domain =  typeof model.domain === 'function'  ? model.domain(self,tmp)  : model.domain;
                        var context = typeof model.context === 'function' ? model.context(self,tmp) : model.context || {};
                        var ids     = typeof model.ids === 'function'     ? model.ids(self,tmp) : model.ids;
                        var order   = typeof model.order === 'function'   ? model.order(self,tmp):    model.order;
                        progress += progress_step;

                        if( model.model ){
                            if(model.model == 'res.partner')
                            {
                                if(model.fields[model.fields-1] != 'loading_data_offline')
                                {
                                    model.fields.push('loading_data_offline');
                                }
                            }
                            if(model.model == 'restaurant.floor')
                            {
                                model.domain = [];
                            }
                            var params = {
                                model: model.model,
                                context: _.extend(context, session.user_context || {}),
                            };

                            if (model.ids) {
                                params.method = 'read';
                                params.args = [ids, fields];
                            } else {
                                params.method = 'search_read';
                                params.domain = domain;
                                params.fields = fields;
                                params.orderBy = order;
                            }

                            rpc.query(params).then(function (result) {
                                try { // catching exceptions in model.loaded(...)
                                    Promise.resolve(model.loaded(self, result, tmp))
                                        .then(function () { load_model(index + 1); },
                                            function (err) { reject(err); });
                                } catch (err) {
                                    console.error(err.message, err.stack);
                                    reject(err);
                                }
                            }, function (err) {
                                reject(err);
                            });
                        } else if (model.loaded) {
                            try { // catching exceptions in model.loaded(...)
                                Promise.resolve(model.loaded(self, tmp))
                                    .then(function () { load_model(index +1); },
                                        function (err) { reject(err); });
                            } catch (err) {
                                reject(err);
                            }
                        } else {
                            load_model(index + 1);
                        }
                    }
                }

                try {
                    return load_model(0);
                } catch (err) {
                    return Promise.reject(err);
                }
            });

            return loaded;
        },
    });
})