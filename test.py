import http.client

conn = http.client.HTTPSConnection("linkedin-data-api.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "d586e7b220msh4c0231f7ff21cd1p169bacjsn04caead9c266",
    'x-rapidapi-host': "linkedin-data-api.p.rapidapi.com"
}

conn.request("GET", "/?username=anagh-dwivedi", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))