# Megalert — MikroTik SMS Gateway

A production-ready SMS gateway that sends alerts via a MikroTik LTE router.  
Supports **Checkmk**, **Home Assistant**, **Uptime Kuma**, and any HTTP client.

---

## Quick Start

### Docker (empfohlen)

```bash
docker run -d -p 5000:5000 \
  -e MIKROTIK_HOST=192.168.10.2 \
  -e MIKROTIK_USER=sms-api \
  -e MIKROTIK_PASS=geheim \
  -e API_TOKEN=dein-token \
  megabitus/megalert
```

### Docker Compose

```bash
cp .env.sample .env
# .env anpassen
docker compose up -d
```

### Lokal

```bash
cp .env.sample .env
# .env anpassen
pip3 install -r requirements.txt
python3 server.py
```

---

## Environment Variables

| Variable | Pflicht | Default | Beschreibung |
|---|---|---|---|
| `MIKROTIK_HOST` | ✅ | — | IP-Adresse des MikroTik Routers |
| `MIKROTIK_USER` | ✅ | — | RouterOS Benutzername |
| `MIKROTIK_PASS` | ✅ | — | RouterOS Passwort |
| `API_TOKEN` | ✅ | — | Bearer Token für die API (`Authorization: Bearer <token>`) |
| `MIKROTIK_PORT` | | `8728` | RouterOS API Port |
| `MIKROTIK_SMS_PORT` | | `lte1` | LTE Interface für SMS-Versand |
| `MEGALERT_HOST` | | `0.0.0.0` | Bind-Adresse der API |
| `MEGALERT_PORT` | | `5000` | Port der API |
| `MEGALERT_DEBUG` | | `false` | Debug-Logging aktivieren |
| `ALLOWED_COUNTRY_CODES` | | *(alle)* | Erlaubte Ländervorwahlen, kommagetrennt (z.B. `49,43`) |
| `MAX_MESSAGE_LENGTH` | | `480` | Maximale Nachrichtenlänge in Zeichen |
| `RATE_LIMIT_PER_MINUTE` | | `10` | Maximale SMS pro Minute |

---

## API

Swagger UI: **http://localhost:5000/apidocs**

### Authentifizierung

Alle Endpoints (außer `/health`) erfordern einen Bearer Token im Header:

```
Authorization: Bearer <API_TOKEN>
```

### Endpoints

#### `POST /api/v1/sms/send` — SMS senden *(primärer Endpoint)*

```bash
curl -X POST http://localhost:5000/api/v1/sms/send \
  -H "Authorization: Bearer dein-token" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+491631272782", "message": "Host DOWN!", "source": "checkmk"}'
```

**Request Body:**

| Feld | Pflicht | Beschreibung |
|---|---|---|
| `phone` | ✅ | Telefonnummer im E.164-Format (z.B. `+491631272782`) |
| `message` | ✅ | Nachrichtentext |
| `source` | | Absender-Bezeichnung für Logging (z.B. `checkmk`) |

**Response `200`:**
```json
{
  "status": "sent",
  "phone": "+491631272782",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-04-30T12:00:00+00:00"
}
```

**Fehlercodes:**

| Code | Bedeutung |
|---|---|
| `400` | Fehlende oder ungültige Felder |
| `401` | Kein oder falscher Bearer Token |
| `403` | Ländervorwahl nicht erlaubt |
| `429` | Rate Limit überschritten |
| `500` | SMS-Zustellung fehlgeschlagen (Modem-Fehler) |
| `503` | MikroTik nicht erreichbar |

---

#### `GET /health` — Health Check

```bash
curl http://localhost:5000/health
# {"status": "ok"}
```

---

#### `POST /api/v1/sms/webhook` — Webhook (Uptime Kuma, generic)

```bash
curl -X POST http://localhost:5000/api/v1/sms/webhook \
  -H "Authorization: Bearer dein-token" \
  -H "phone: +491631272782" \
  -H "Content-Type: application/json" \
  -d '{"msg": "Service DOWN"}'
```

---

#### `POST /api/v1/sms` *(deprecated)* / `GET /api/v1/sms`

Legacy-Endpoints, die noch funktionieren aber nicht mehr empfohlen werden.  
`GET /api/v1/sms` liest den SMS-Eingang des MikroTik (muss in RouterOS aktiviert sein: `/tool sms set receive-enabled=yes`).

---

## Checkmk Integration

Script unter [checkmk-notify-sms.sh](checkmk-notify-sms.sh) liegt bereits im Repo.

**Setup:**

```bash
# Script auf den Checkmk-Server kopieren
cp checkmk-notify-sms.sh /omd/sites/<site>/local/share/check_mk/notifications/notify-sms
chmod +x /omd/sites/<site>/local/share/check_mk/notifications/notify-sms
```

**Umgebungsvariablen auf dem Checkmk-Server setzen:**

```bash
export SMS_GATEWAY_URL=http://192.168.10.10:5000
export SMS_API_TOKEN=dein-token
```

**Checkmk Notification Rule:**
- Notification method: `notify-sms`
- Contact → Pager address: Telefonnummer im E.164-Format (z.B. `+491631272782`)

---

## Home Assistant Integration

```yaml
# configuration.yaml
rest_command:
  send_sms:
    url: "http://192.168.10.10:5000/api/v1/sms/send"
    method: POST
    headers:
      Authorization: "Bearer dein-token"
      Content-Type: application/json
    payload: '{"phone": "{{ phone }}", "message": "{{ message }}", "source": "home-assistant"}'
```

**Automation Beispiel:**

```yaml
action:
  - service: rest_command.send_sms
    data:
      phone: "+491631272782"
      message: "Türklingel betätigt!"
```

---

## Sicherheitshinweise

- `API_TOKEN` nie in die Versionskontrolle einchecken — `.env` ist in `.gitignore`
- MikroTik-Benutzer mit minimalen Rechten anlegen (nur `/tool/sms` und `/log`)
- `ALLOWED_COUNTRY_CODES` setzen um unerwünschte Empfänger zu blockieren
- `RATE_LIMIT_PER_MINUTE` schützt vor Alarm-Stürmen

---

## Disclaimer

_Megalert comes with ABSOLUTELY NO WARRANTY, to the extent permitted by applicable law._

## License

Distributed under the [MIT License](LICENSE).
