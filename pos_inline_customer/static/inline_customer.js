odoo.define('pos_inline_customer.ActionPadWithInlineCustomer', function(require) {
    'use strict';
    let rpc = require('web.rpc');
    // const { ClientListScreen } = require('point_of_sale.tour.ClientListScreenTourMethods');
    $(function(){
         $('.search_customers').keyup(function(){
            let kw = $(this).val();
            console.log(kw, 11);
            if(kw){
                console.log('searching', kw);
                load_customers(kw);
            }
        }).change(function(){
            //ClientListScreen.exec.setClient('Azure Interior');
//            $('.clientlist-screen .client-list-contents .client-line td:contains('++')')
            console.log(11, $('.clientlist-screen .client-list-contents .client-line').length);
            console.log('waoo');
        });


        let last_tried_kw = '';
        let last_searched_kw = '';
        let loading_customers = false;

        load_customers('');
        function load_customers(kw){
            let limit = 100;
            if(!kw){
                kw = 'a';
            }
            else{
                limit = 16;
            }
            if(loading_customers){
                last_tried_kw = kw;
                return;
            }
            loading_customers = true;
            last_tried_kw  = last_searched_kw = kw;
            let domain = [['name','like', '%'+kw+'%']];
            let rpc_args = [domain, ['id', 'name']];
            rpc.query({
                model: 'res.partner',
                method: 'search_read',
                args: rpc_args,
                limit: 100,
                order: 'name'
            }).then(function (partners) {
                console.log(partners);
                let ar_data = [];
                for(let item of partners){
                    ar_data.push({id: item.id, text: item.name});
                }
                $(".search_customers").empty();
                $(".search_customers").select2({
                    placeholder: 'Select an option',
                    data: ar_data,
                    allowClear: true,
                    width: 180
                });
                $('.select2-focusser.select2-offscreen').hide();
                loading_customers = false;
                if(last_tried_kw != last_searched_kw){
                    load_customers(last_tried_kw);
                }
            });
        }
    });


//    const Registries = require('point_of_sale.Registries');
//    class ActionPadWithInlineCustomer {
//    }
//
//    ActionPadWithInlineCustomer.template = 'ActionPadWithInlineCustomer';
//    Registries.Component.add(ActionPadWithInlineCustomer);
//    return ActionPadWithInlineCustomer;
});

//odoo.define('pos_inline_customer.ClientScreen', function(require) {
//    'use strict';
//
//    const PosClientScreen = require('point_of_sale.ClientListScreen');
//    const Registries = require('point_of_sale.Registries');
//
//    class ClientScreen extends PosClientScreen {
//        updateClientList(event) {
//            this.state.query = event.target.value;
//            const clients = this.clients;
//            console.log('updates updated 222');
//            if (event.code === 'Enter' && clients.length === 1) {
//                this.state.selectedClient = clients[0];
//                this.clickNext();
//            } else {
//                this.render();
//            }
//        }
//        clickClient(event) {
//            let partner = event.detail.client;
//            console.log('updates added 111');
//            if (this.state.selectedClient === partner) {
//                this.state.selectedClient = null;
//            } else {
//                this.state.selectedClient = partner;
//            }
//            this.render();
//        }
//    }
//    Registries.Component.add(ClientScreen);
//    console.log('updates added');
//    return ClientScreen;
//});
//
