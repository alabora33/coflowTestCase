import json
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

class StockConnector(models.AbstractModel):
    _name = "field_service_visit.stock_connector"
    _description = "FastAPI Stock Connector"

    def _get_config(self):
        ICP = self.env["ir.config_parameter"].sudo()
        base = ICP.get_param("field_service_visit.fastapi_base_url") or "http://127.0.0.1:8000"
        key = ICP.get_param("field_service_visit.fastapi_api_key") or ""
        loc_id = ICP.get_param("field_service_visit.stock_location_id")
        location = self.env["stock.location"].browse(int(loc_id)) if (loc_id and loc_id.isdigit()) else False
        return base, key, location

    def sync_bulk(self):
        """Tek request ile bulk stok çek → product.default_code == sku eşleştir → stock.quant güncelle."""
        base, key, location = self._get_config()
        if not base or not key or not location:
            raise ValueError("FastAPI base/api_key/location config is missing")

        # requests yerine odoo'nun builtin'ini kullan (proxy/ssl uyumu için iyi pratik)
        http = self.env["ir.http"]
        url = f"{base}/api/v1/stock/bulk"
        headers = {"X-API-KEY": key}

        try:
            # Odoo'da requests yoksa: pip ile requests ekleyebilirsin (requirements.txt)
            import requests
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                _logger.error("Bulk sync failed: %s %s", resp.status_code, resp.text)
                return {"ok": False, "status": resp.status_code, "error": resp.text}

            data = resp.json()  # [{'sku': 'SKU001', 'qty': 12}, ...]
            sku_to_qty = {item["sku"]: item["qty"] for item in data if "sku" in item and "qty" in item}

            # Ürünleri tek seferde çek
            products = self.env["product.product"].sudo().search([("default_code", "in", list(sku_to_qty.keys()))])
            if not products:
                return {"ok": True, "updated": 0, "skipped": len(sku_to_qty), "detail": "no matching products"}

            # Mevcut quant kayıtlarını çek (location bazlı)
            quants = self.env["stock.quant"].sudo().search([
                ("product_id", "in", products.ids),
                ("location_id", "=", location.id),
            ])

            # Hızlı erişim için mapping
            quant_map = {(q.product_id.id, q.location_id.id): q for q in quants}

            updates = []
            created = 0
            for prod in products:
                target_qty = float(sku_to_qty.get(prod.default_code, 0))
                key = (prod.id, location.id)
                if key in quant_map:
                    q = quant_map[key]
                    if q.quantity != target_qty:
                        updates.append((q, target_qty))
                else:
                    # quant yoksa create
                    self.env["stock.quant"].sudo().create({
                        "product_id": prod.id,
                        "location_id": location.id,
                        "quantity": target_qty,
                    })
                    created += 1

            # Batch write (performans)
            for q, newqty in updates:
                q.sudo().write({"quantity": newqty})

            return {"ok": True, "updated": len(updates), "created": created, "skipped": len(sku_to_qty) - len(products)}

        except Exception as e:
            _logger.exception("Bulk sync exception: %s", e)
            return {"ok": False, "error": str(e)}
