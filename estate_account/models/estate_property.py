from odoo import models, Command


class InheritedModel(models.Model):
    _inherit = "estate.property"

    def action_sold_property(self):
        for record in self:
            values = {
                "partner_id": record.buyer_id.id,
                "move_type": "out_invoice",
                "line_ids": [
                    Command.create({
                        "name": record.name,
                        "quantity": 1,
                        "price_unit": record.selling_price * 0.06,
                    }),
                    Command.create({
                        "name": "Administrative fees",
                        "quantity": 1,
                        "price_unit": 100.00,
                    }),
                ],
            }
            self.env["account.move"].create(values)
        return super().action_sold_property()
