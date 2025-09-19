# FastAPI Stock Service

## Kurulum

```bash
cd fastapi_app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

.env dosyasına bir API_KEY tanımlayın:
```
API_KEY=devkey
```

## Çalıştırma

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpointler

- `GET /api/v1/stock?sku=SKU001` → `{ "sku": "SKU001", "qty": 12 }`
- `GET /api/v1/stock/bulk` → `[ { "sku": "SKU001", "qty": 12 }, ... ]`

Tüm isteklerde header olarak `X-API-KEY` gönderilmelidir.

## Örnek Çağrı

```bash
curl -H "X-API-KEY: devkey" "http://localhost:8000/api/v1/stock?sku=SKU001"
curl -H "X-API-KEY: devkey" "http://localhost:8000/api/v1/stock/bulk"
```

## Odoo Entegrasyonu

- Odoo admin panelinden FastAPI URL ve API key ayarlarını girin.
- "Sync Stock from FastAPI" action/wizard ile toplu stok güncellemesi başlatılır.
- Hatalar ve sonuçlar wizard ekranında gösterilir.

