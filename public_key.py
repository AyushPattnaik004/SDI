import requests
import json

url = "https://backend.aisensy.com/direct-apis/t1/whatsapp-business-encryption"

payload = {"businessPublicKey": """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAv6fpHxMmYlW3GkyS0dr4
uCQEC2ptMp0sg2/wPErpNOsKis7i8rOqMUes8u9jllAix87kwEDpdIuq313wKbo8
AcJMtOcXb8tVdxZDK/zMxNw3KC0OUDW5z4QirTPWI+5QrXP6D6EvU3VnRUV8jMBr
hqqW4+X6AKpZ5LGLpA3FKmj+QZrIOq2Bp3fVG/HzCcsasx5c+x9LvBusUo69Ybf+
hkgLkZBOHfFTySvWwaWQxNMryp44NE0v31Hb8iEyUHUBNxTSzxpEE/BjVnBgHYvD
/zetUy1aAzCW9b56RWueCHUlxBcI2nhbX6Bdvug38kX2zYN0GzrV5CYnxWYd/z8a
JwIDAQAB
-----END PUBLIC KEY-----
""" }
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhc3Npc3RhbnRJZCI6IjZhMDQyM2E5ZDI4YTRjMzNkMTIxOWQ2ZSIsImNsaWVudElkIjoiNjg5YjczNmEwYWJmZTYyNmRkMDQwMmQwIiwiaWF0IjoxNzc4NjU3Njk3fQ.K03wN3Tg_qBPh8YGJ8AxNwhjaWMkP7FCf8DZyUmIiv8',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

print(response.text)