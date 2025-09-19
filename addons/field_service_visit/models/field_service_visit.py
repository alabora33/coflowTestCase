# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class FieldServiceVisit(models.Model):
	def _cron_notify_tomorrow_visits(self):
		from datetime import datetime, timedelta
		tomorrow = (fields.Datetime.now() + timedelta(days=1)).date()
		start = fields.Datetime.to_string(datetime.combine(tomorrow, datetime.min.time()))
		end = fields.Datetime.to_string(datetime.combine(tomorrow, datetime.max.time()))
		visits = self.search([
			('date_start', '>=', start),
			('date_start', '<=', end),
			('state', 'in', ['planned', 'in_progress'])
		])
		employees = visits.mapped('employee_id')
		for emp in employees:
			user = emp.user_id
			if user and user.email:
				emp_visits = visits.filtered(lambda v: v.employee_id == emp)
				body = '<ul>' + ''.join([f'<li>{v.name} ({v.date_start} - {v.date_end})</li>' for v in emp_visits]) + '</ul>'
				self.env['mail.mail'].sudo().create({
					'subject': 'Tomorrow Visits',
					'body_html': f'<p>Dear {emp.name},</p><p>Tomorrow you have the following visits:</p>{body}',
					'email_to': user.email,
				}).send()

	def action_set_planned_and_notify(self):
		for rec in self:
			rec.state = 'planned'
			template = self.env.ref('field_service_visit.mail_template_visit_planned', raise_if_not_found=False)
			if template:
				template.send_mail(rec.id, force_send=True)
	_name = 'field.service.visit'
	_description = 'Field Service Visit'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='Visit Name', required=True, tracking=True)
	customer_id = fields.Many2one(
		'res.partner', string='Customer', required=True,
		domain="[('is_company','=',True)]", tracking=True
	)
	employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
	date_start = fields.Datetime(string='Start Date', required=True, tracking=True)
	date_end = fields.Datetime(string='End Date', required=True, tracking=True)
	duration_hours = fields.Float(string='Duration (hours)', compute='_compute_duration', store=True)
	state = fields.Selection([
		('draft', 'Draft'),
		('planned', 'Planned'),
		('in_progress', 'In Progress'),
		('done', 'Done'),
		('cancel', 'Cancelled'),
	], string='Status', default='draft', tracking=True)
	notes = fields.Text(string='Notes')

	@api.depends('date_start', 'date_end')
	def _compute_duration(self):
		for rec in self:
			if rec.date_start and rec.date_end and rec.date_end > rec.date_start:
				delta = rec.date_end - rec.date_start
				rec.duration_hours = delta.total_seconds() / 3600.0
			else:
				rec.duration_hours = 0.0

	@api.constrains('date_start', 'date_end')
	def _check_dates(self):
		for rec in self:
			if rec.date_end and rec.date_start and rec.date_end < rec.date_start:
				raise ValidationError(_('End date cannot be before start date.'))

	@api.constrains('employee_id', 'state')
	def _check_employee_required(self):
		for rec in self:
			if rec.state != 'draft' and not rec.employee_id:
				raise ValidationError(_('Employee is required except in draft state.'))

	def action_set_planned(self):
		for rec in self:
			rec.state = 'planned'

	def action_set_in_progress(self):
		for rec in self:
			rec.state = 'in_progress'

	def action_set_done(self):
		for rec in self:
			rec.state = 'done'

	def action_set_cancel(self):
		for rec in self:
			rec.state = 'cancel'
