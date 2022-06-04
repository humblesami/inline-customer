odoo.define('pl.index', function(require) {
    'use strict';
    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;

    let special_pl_name = 'Special';
    let threshold_amount = 5000;
    models.Order = models.Order.extend({
        get_total_with_tax: function() {
            let self = this;
            let res = this.get_total_without_tax() + this.get_total_tax();
            if(self.pos.config.special_price_list)
            {
                console.log(self.pos.config.special_price_list.name);
            }
            if(res > threshold_amount){
                if(self.pricelist.name != special_pl_name){
                    //Option 1
                    //self.set_pricelist(self.pos.config.special_price_list);
                    //res = this.get_total_without_tax() + this.get_total_tax();

                    //Option2
                    // search pricelist by a static name
                    let found = 0;
                    console.log('before => ' + self.pricelist.name + ' is selected');
                    for(let pl of self.pos.pricelists){
                        if(pl.name == special_pl_name){
                            found = 1;
                            self.set_pricelist(pl);
                            console.log('after => ' + self.pricelist.name + ' is selected');
                            res = this.get_total_without_tax() + this.get_total_tax();
                            break;
                        }
                    }
                    if(!found){
                        console.log('Please add a price list with name => '+special_pl_name);
                    }
                }
                else{
                    console.log('Already selected => ' + self.pricelist.name + ' because order was gone above '+threshold_amount);
                }
            }
            else{
                if(self.pricelist.name == special_pl_name){
                    self.set_pricelist(self.pos.default_pricelist)
                }
            }
            return res;
        },
    });
});