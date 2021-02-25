odoo.define('pos.models', function (require) {

var models = require('point_of_sale.models');

models.load_models([{
    model:  'l10n_latam.identification.type',
    fields: ['name', 'sequence'],
    /*
    domain: function(self){ return [['name','in',['VAT','Passport','Foreign ID']]]; },
    */

    domain: function(self){ return ['|','|',
                                    ['name','=','VAT'],
                                    ['name','=','Pasaporte'],
                                    ['name', '=','Cédula Extranjera']
                                   ]; },

    loaded: function(self, types) {
        self.types = types;
    }

}]);
/*
pos_model.load_fields('res.partner', 'l10n_latam_identification_type_id');
*/

models.load_models([{
    model:  'res.partner',
        fields: ['l10n_latam_identification_type_id'],

    loaded: function(self, partner) {
    }
}]);



});
