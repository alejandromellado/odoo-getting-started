from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Multiple tags can be associated to multiple properties to aid description and search.'
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    # Constraints
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'A property tag name must be unique')
    ]
