odoo.define('pl.index', function(require) {
    'use strict';

    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;

    console.log('Price list selection/change');
    let threshold_amount = 5000;
    let special_pricelist = undefined;

    models.Order = models.Order.extend({
        get_total_with_tax: function() {
            let self = this;
            let res = this.get_total_without_tax() + this.get_total_tax();
            threshold_amount = self.pos.config.effective_amount;
            if(!special_pricelist){
                special_pricelist = self.pos.config.applied_pricelist;
                if(!special_pricelist){
                    console.log('No applied price list ', self.pos.config);
                    return res;
                }
                // Following lines are hack because dont know yet how to get full object directly in
                // self.pos.config.applied_pricelist
                if(Array.isArray(special_pricelist)){
                    let filtered_array = self.pos.pricelists.filter(function(item){
                        return special_pricelist[0] == item.id;
                    });
                    special_pricelist = filtered_array[0];
                }
                console.log(special_pricelist);
                //Now special_pricelist is object with all properties
            }

            if(res < threshold_amount){
                if(self.pricelist.id != self.pos.default_pricelist.id){
                    self.set_pricelist(self.pos.default_pricelist);
                    console.log(self.pricelist.name + ' is selected back');
                }
                return res;
            }
            if(self.pricelist.id != special_pricelist.id){
                let found = 0;
                self.set_pricelist(special_pricelist);
                console.log(self.pricelist.name + ' is now selected');
                res = this.get_total_without_tax() + this.get_total_tax();
            }
            return res;
        },
    });
});