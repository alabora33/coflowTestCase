# coflowTestCase

![CI](https://github.com/alabora33/coflowTestCase/actions/workflows/ci.yml/badge.svg)

## Test ve CI

CI pipeline otomatik olarak kod stilini (flake8, black) ve Odoo testlerini çalıştırır.

### Örnek Test Çıktısı

```
Test module: field_service_visit.tests.test_visit
.
----------------------------------------------------------------------
Ran 5 tests in 2.345s

OK
```

## Kurulum & Konfigürasyon

### Gereksinimler
- Ubuntu 22.04
- Python 3.10+
- PostgreSQL 14+

### 1. Sistem Kullanıcısı ve Ortam Kurulumu
```bash
sudo adduser --system --home=/opt/odoo --group odoo
sudo apt update && sudo apt install python3-venv python3-pip git postgresql -y
sudo -u odoo -H python3 -m venv /opt/odoo/venv
sudo -u odoo -H /opt/odoo/venv/bin/pip install wheel
```

### 2. PostgreSQL Ayarları
```bash
sudo -u postgres createuser --createdb odoo17
sudo -u postgres psql -c "ALTER USER odoo17 WITH PASSWORD 'MASKED_PASSWORD';"
```

### 3. Odoo Kaynak Kodunu Klonla
```bash
git clone https://github.com/odoo/odoo.git -b 17.0 odoo-src
```

### 4. Python Bağımlılıkları
```bash
sudo -u odoo -H /opt/odoo/venv/bin/pip install -r odoo-src/requirements.txt
```

### 5. odoo.conf Ayarları (örnek, maskelenmiş)
```ini
[options]
addons_path = ./odoo-src/addons,./addons
data_dir    = ./odoo-data
db_host     = 127.0.0.1
db_port     = 5432
db_user     = odoo17
db_password = MASKED_PASSWORD
http_port   = 8069
workers     = 2  # (CPU çekirdeği x 2) + 1 önerilir. 2 çekirdek için 2 worker mantıklı.
proxy_mode  = True  # Reverse proxy (nginx) arkasında çalışacaksa True olmalı.
log_level   = info
limit_time_real = 120
admin_passwd = MASKED_ADMIN_PASS
without_demo = all
```

**Açıklamalar:**
- `workers`: (Çekirdek x 2) + 1 formülü önerilir. 2 çekirdekli bir makinede 2 worker idealdir. Geliştirme ortamında 0 (tek iş parçacığı) da olabilir.
- `proxy_mode`: Odoo bir reverse proxy (örn. nginx) arkasında çalışacaksa True olmalı.
- `limit_time_real`: Her bir HTTP isteği için maksimum süre (saniye).
- `log_level`: info, debug, warning, error seviyeleri kullanılabilir.

### 6. Systemd Servis Dosyası (deploy/odoo.service)
```ini
[Unit]
Description=Odoo 17 Service
After=network.target

[Service]
Type=simple
User=odoo
WorkingDirectory=/opt/odoo
ExecStart=/opt/odoo/venv/bin/python /opt/odoo/odoo-src/odoo-bin -c /opt/odoo/odoo.conf
Restart=always

[Install]
WantedBy=multi-user.target
```

**Açıklamalar:**
- `User`: Odoo için oluşturulan sistem kullanıcısı.
- `WorkingDirectory`: Odoo'nun ana dizini.
- `ExecStart`: Odoo'yu sanal ortamda başlatır.

### 7. Logrotate Ayarı
Odoo loglarının büyümemesi için logrotate önerilir. Örnek config:
```bash
/var/log/odoo/*.log {
	copytruncate
	missingok
	notifempty
	rotate 7
	daily
	compress
}
```
Bu dosyayı `/etc/logrotate.d/odoo` olarak ekleyebilirsiniz.

### 8. Temel Modüllerin Yüklenmesi
Odoo arayüzünden yeni bir veritabanı oluşturup, `base`, `web`, `sale`, `stock` modüllerini yükleyin.

### 9. Şirket ve Para Birimi Ayarları
Şirket bilgilerini ve para birimini ayarlayın. Geliştirici modunu açmak için: Ayarlar > Geliştirici Modu.

### 10. Reverse Proxy Notları
Odoo'yu doğrudan internete açmak yerine nginx gibi bir reverse proxy arkasında çalıştırmak güvenlik ve performans için önerilir. `proxy_mode = True` olmalı.

---

## Performans: EXPLAIN ANALYZE ve İndeks Önerisi

Örnek domain araması:
```sql
EXPLAIN ANALYZE SELECT * FROM field_service_visit WHERE employee_id = 5 AND state = 'planned';
```
Örnek çıktı:
```
Seq Scan on field_service_visit  (cost=0.00..35.50 rows=5 width=...) (actual time=0.021..0.045 rows=2 loops=1)
  Filter: ((employee_id = 5) AND (state = 'planned'))
  Rows Removed by Filter: 98
Planning Time: 0.120 ms
Execution Time: 0.060 ms
```
Eğer tablo büyürse, bu sorgu için aşağıdaki gibi bir indeks önerilir:
```sql
CREATE INDEX idx_field_service_visit_employee_state ON field_service_visit (employee_id, state);
```
Bu sayede ilgili domain aramaları çok daha hızlı çalışır.

---

## Kod Stili ve CI

- Kod stili için [flake8](https://flake8.pycqa.org/) ve [black](https://black.readthedocs.io/) kullanılır.
- CI pipeline'da otomatik olarak `flake8` ve `black --check` çalışır.
- Geliştirici olarak kodunuzu göndermeden önce:

```bash
pip install flake8 black
flake8 addons/field_service_visit fastapi_app
black --check addons/field_service_visit fastapi_app
```

Ayrıca, Odoo testleri için:

```bash
python odoo-src/odoo-bin -c odoo.conf -d odoo_test --test-enable -i field_service_visit --stop-after-init
```

Her adım tekrarlanabilir ve otomasyona uygundur. Sorularınız için: [Odoo Docs](https://www.odoo.com/documentation/17.0/)