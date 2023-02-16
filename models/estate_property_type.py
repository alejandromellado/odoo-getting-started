from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Represents the type of property that is listed.'

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id')

    # Constraints
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'A property type name must be unique')
    ]
