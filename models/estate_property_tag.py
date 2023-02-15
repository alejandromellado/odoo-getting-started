from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Multiple tags can be associated to multiple properties to aid description and search.'

    name = fields.Char(required=True)

    # Constraints
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'A property tag name must be unique')
    ]
