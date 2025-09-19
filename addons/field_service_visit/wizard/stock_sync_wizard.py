from odoo import api, fields, models, _

class StockSyncWizard(models.TransientModel):
    _name = 'field.service.visit.stock.sync.wizard'
    _description = 'Stock Sync Wizard'

    result_message = fields.Text(string="Result", readonly=True)

    def action_sync(self):
        connector = self.env['field_service_visit.stock_connector']
        result = connector.sync_bulk()
        msg = _("Sync completed. Updated: %s, Created: %s, Skipped: %s") % (
            result.get('updated', 0), result.get('created', 0), result.get('skipped', 0)
        ) if result.get('ok') else _("Sync failed: %s") % result.get('error')
        self.result_message = msg
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
