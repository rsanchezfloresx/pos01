odoo.define('pos.member', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var _super_posmodel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function (model){
                return model.model === 'res.partner';
            });
            partner_model.fields.push('membership_code');
            return _super_posmodel.initialize.call(this, session, attributes);
        },
    });
});