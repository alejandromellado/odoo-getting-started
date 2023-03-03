from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged, Form


# The CI will run these tests after all the modules are installed,
# not right after installing the one defining it.
@tagged('post_install', '-at_install')
class EstateTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        # add env on cls and many other things
        super(EstateTestCase, cls).setUpClass()

        # create the data for each test. By doing it in the setUpClass instead
        # of in a setUp or in each test case, we reduce the testing time and
        # the duplication of code.
        cls.buyer = cls.env['res.partner'].create({
            'name': 'buyer',
        })
        cls.properties = cls.env['estate.property'].create([{
            'name': 'prop1',
            'expected_price': 10000,
        }])
        cls.offers = cls.env['estate.property.offer'].create([{
            'partner_id': cls.buyer.id,
            'property_id': cls.properties[0].id,
            'price': 9000,
        }])

    def test_action_sell(self):
        """Test that everything behaves like it should when selling a property."""
        # You cannot sell a property without an accepted offer
        with self.assertRaises(UserError):
            self.properties.action_sold_property()

        # Accept an offer for this property
        self.offers.action_accept_offer()

        # Try to mark the property as sold again
        self.properties.action_sold_property()
        self.assertRecordValues(self.properties, [
            {'state': 'sold'},
        ])

        # You cannot create an offer for a sold property
        with self.assertRaises(UserError):
            self.env['estate.property.offer'].create([{
                'partner_id': self.buyer.id,
                'property_id': self.properties[0].id,
                'price': 10000,
            }])

    def test_property_form(self):
        """Test the form view of properties."""
        with Form(self.properties[0]) as prop:
            # Check that garden related values reset when garden is set to False
            self.assertEqual(prop.garden_area, 0)
            self.assertIs(prop.garden_orientation, False)

            prop.garden = True
            self.assertEqual(prop.garden_area, 10)
            self.assertIs(prop.garden_orientation, 'north')

            prop.garden = False
            self.assertEqual(prop.garden_area, 0)
            self.assertIs(prop.garden_orientation, False)
