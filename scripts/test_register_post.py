import json
import urllib.request

url = 'http://127.0.0.1:8000/api/register/'
payload = {
  "nombres": "pedro",
  "apellidos": "pereira",
  "email": "prueba1@mail.com",
  "password": "cliente123",
  "password_confirm": "cliente123",
  "telefono": "75695707",
  "fecha_nacimiento": "1997-05-02",
  "genero": "M",
  "documento_identidad": "9760600",
  "pais": "Bolivia",
  "rol": 2
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode('utf-8')
        print('STATUS', resp.status)
        print('BODY', body)
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print('STATUS', e.code)
    print('BODY', body)
except Exception as ex:
    print('ERROR', ex)
