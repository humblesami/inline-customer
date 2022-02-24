odoo.define('inline_customer_pos.InlineCustomerWidget', function(require) {
    'use strict';
    let rpc = require('web.rpc');
    var models = require('point_of_sale.models');

    models.PosModel = models.PosModel.extend({
        after_load_server_data: function(){
            this.load_orders();
            this.set_start_order();
            let pos_model = this;
            console.log(333);
            selected_client = pos_model.get_order().get_client();
            $(function(){
                load_partners_drop_down(pos_model);
            });
            $('body').on('click', '.btn-switchpane.secondary', function(){
                setTimeout(function(){
                    load_partners_drop_down(pos_model);
                }, 100);
            });
            if(this.config.use_proxy){
                if (this.config.iface_customer_facing_display) {
                    this.on('change:selectedOrder', this.send_current_order_to_customer_facing_display, this);
                }
                return this.connect_to_proxy();
            }
            return Promise.resolve();
        },
        get_client: function(){
            //its called each time screen changed,
            //should not be called until partners are loaded once via after_load_server_data (first time)
            if(once_loaded && !$('.select2-focusser.select2-offscreen').length){
                triggered_on_load = 0;
                load_partners_drop_down(this);
            }
            var order = this.get_order();
            if (order) {
                return order.get_client();
            }
            return null;
        },
    });

    let once_loaded = 0;
    let last_order = null;
    let triggered_on_load = 0;
    let selected_client = null;

    let search_fields = ['name', 'email'];
    let show_all_search_fields_in_text = true;

    function load_partners_drop_down(pos_model){
        let input_found = $(".search_customers").length;
        console.log('button there', input_found);
        if(input_found){
            if(!input_found){
                return;
            }
        }
        once_loaded = 1;
        let partners_array = pos_model.partners;

        set_display_text(partners_array, show_all_search_fields_in_text, search_fields);
        $(".search_customers").empty();
        $(".search_customers").select2({
            placeholder: 'Select an option',
            data: partners_array,
            allowClear: true,
            width: 180,
            matcher: matcher_function
        }).change(function(){
            if(!triggered_on_load){
                let dd_client1 = $(".search_customers").select2('data');
                pos_model.get_order().set_client(dd_client1);
                selected_client = dd_client1;
            }
            triggered_on_load = 0;
        });
        $('.select2-focusser.select2-offscreen').hide();
        selected_client = pos_model.get_order().get_client();
        sync_the_drop_down_with_selected_client_in_order();
    }

    //this was the actually new required function along with get_client in models.PosModel
    function sync_the_drop_down_with_selected_client_in_order(){
        let dd_client2 = $(".search_customers").select2('data');
        if(selected_client){
            if(!dd_client2){
                triggered_on_load = 1;
                $(".search_customers").val(selected_client.id).change();
            }
            else if(dd_client2.id != selected_client.id){
                triggered_on_load = 1;
                $(".search_customers").val(selected_client.id).change();
            }
        }
        else{
            if(dd_client2){
                $(".search_customers").val('');
            }
        }
    }

    function matcher_function(term, text, option) {
        if(search_fields && Array.isArray(search_fields) && search_fields.length){
            for(let field of search_fields){
                let res = option[field].toUpperCase().indexOf(term.toUpperCase()) > -1;
                if(res){
                    return res;
                    //other wise keep looking into next fields
                }
            }
        }
        else{
            return text.toUpperCase().indexOf(term.toUpperCase()) > -1;
        }
    }

    function set_display_text(partners_array, show_all_search_fields_in_text, search_fields){
        for(let item of partners_array){
            item.text = '';
            if(show_all_search_fields_in_text){
                for(let field of search_fields){
                    if(item.text)
                    {
                        item.text += ' - ' + item[field];
                    }
                    else{
                        item.text = item[field];
                    }
                }
            }
            else{
                item.text = item.name;
            }
        }
        // no need to return because it is passed by reference so original array is changed
        return partners_array;
    }
});
