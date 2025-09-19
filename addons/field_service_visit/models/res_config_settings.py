from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fastapi_base_url = fields.Char(string="FastAPI Base URL")
    fastapi_api_key = fields.Char(string="FastAPI API Key")
    stock_location_id = fields.Many2one("stock.location", string="Default Location")

    def set_values(self):
        res = super().set_values()
        IrConfig = self.env["ir.config_parameter"].sudo()
        IrConfig.set_param("field_service_visit.fastapi_base_url", self.fastapi_base_url or "")
        IrConfig.set_param("field_service_visit.fastapi_api_key", self.fastapi_api_key or "")
        IrConfig.set_param("field_service_visit.stock_location_id", self.stock_location_id.id or False)
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        IrConfig = self.env["ir.config_parameter"].sudo()
        res.update(
            fastapi_base_url=IrConfig.get_param("field_service_visit.fastapi_base_url", default="http://127.0.0.1:8000"),
            fastapi_api_key=IrConfig.get_param("field_service_visit.fastapi_api_key", default="secret123"),
        )
        loc_id = IrConfig.get_param("field_service_visit.stock_location_id")
        res["stock_location_id"] = int(loc_id) if loc_id and loc_id.isdigit() else False
        return res
