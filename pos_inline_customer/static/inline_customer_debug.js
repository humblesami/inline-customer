odoo.define('pos_inline_customer.InlineCustomer', function(require) {
    'use strict';
    let rpc = require('web.rpc');
    var models = require('point_of_sale.models');

    models.PosModel = models.PosModel.extend({
        after_load_server_data: function(){
            this.load_orders();
            this.set_start_order();

            let pos_model = this;
            $(function(){
                load_partners_drop_down(pos_model);
            });

            if(this.config.use_proxy){
                if (this.config.iface_customer_facing_display) {
                    this.on('change:selectedOrder', this.send_current_order_to_customer_facing_display, this);
                }
                return this.connect_to_proxy();
            }
            return Promise.resolve();
        },
    });

    function load_partners_drop_down(pos_model){
        let ar_data = pos_model.partners;
        for(let item of ar_data){
            item.text = item.name;
        }
        $(".search_customers").empty();
        $(".search_customers").select2({
            placeholder: 'Select an option',
            data: ar_data,
            allowClear: true,
            width: 180
        }).change(function(){
            let select_item = $(".search_customers").select2('data');
            console.log(select_item, ' is selected as cutomer');
            pos_model.get_order().set_client(select_item);
        });
        $('.select2-focusser.select2-offscreen').hide();
    }
});
