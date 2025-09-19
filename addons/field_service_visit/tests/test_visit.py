import pytest
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class TestFieldServiceVisit(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({'name': 'Test Customer', 'customer_rank': 1})
        self.employee = self.env['hr.employee'].create({'name': 'Test Employee'})
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser',
            'email': 'testuser@example.com',
        })
        self.employee.user_id = self.user.id

    def test_create_valid_visit(self):
        visit = self.env['field.service.visit'].create({
            'name': 'Visit 1',
            'customer_id': self.partner.id,
            'employee_id': self.employee.id,
            'date_start': datetime.now(),
            'date_end': datetime.now() + timedelta(hours=2),
        })
        self.assertEqual(visit.state, 'draft')
        self.assertGreater(visit.duration_hours, 0)

    def test_constraint_end_before_start(self):
        with self.assertRaises(ValidationError):
            self.env['field.service.visit'].create({
                'name': 'Visit 2',
                'customer_id': self.partner.id,
                'employee_id': self.employee.id,
                'date_start': datetime.now(),
                'date_end': datetime.now() - timedelta(hours=2),
            })

    def test_employee_required_except_draft(self):
        visit = self.env['field.service.visit'].create({
            'name': 'Visit 3',
            'customer_id': self.partner.id,
            'employee_id': self.employee.id,
            'date_start': datetime.now(),
            'date_end': datetime.now() + timedelta(hours=1),
        })
        visit.employee_id = False
        visit.state = 'planned'
        with self.assertRaises(ValidationError):
            visit._check_employee_required()

    def test_state_flow(self):
        visit = self.env['field.service.visit'].create({
            'name': 'Visit 4',
            'customer_id': self.partner.id,
            'employee_id': self.employee.id,
            'date_start': datetime.now(),
            'date_end': datetime.now() + timedelta(hours=1),
        })
        visit.action_set_planned()
        self.assertEqual(visit.state, 'planned')
        visit.action_set_in_progress()
        self.assertEqual(visit.state, 'in_progress')
        visit.action_set_done()
        self.assertEqual(visit.state, 'done')

    def test_server_action_mail(self):
        visit = self.env['field.service.visit'].create({
            'name': 'Visit 5',
            'customer_id': self.partner.id,
            'employee_id': self.employee.id,
            'date_start': datetime.now(),
            'date_end': datetime.now() + timedelta(hours=1),
        })
        # Should not raise
        visit.action_set_planned_and_notify()
