import requests

FLASK_API = "http://localhost:5000"

# Register converters
requests.post(f"{FLASK_API}/registerConversion", json={
    "serviceAddress": "internal",
    "sourceFormat": "JsonSchema",
    "targetFormat": "LinkMl",
    "supportedFeatures": ["Comments", "Properties", "Attributes"]
})

requests.post(f"{FLASK_API}/registerConversion", json={
    "serviceAddress": "internal",
    "sourceFormat": "LinkMl",
    "targetFormat": "OntologyRdf",
    "supportedFeatures": ["Hierarchy", "References"]
})

requests.post(f"{FLASK_API}/registerConversion", json={
    "serviceAddress": "http://java-service:8080",
    "sourceFormat": "JsonSchema",
    "targetFormat": "Xsd",
    "supportedFeatures": ["Properties"]
})

requests.post(f"{FLASK_API}/registerConversion", json={
    "serviceAddress": "http://node-service:3001",
    "sourceFormat": "Xsd",
    "targetFormat": "MdModels",
    "supportedFeatures": ["Attributes", "Composition"]
})

# Trigger conversion
r = requests.post(f"{FLASK_API}/convert", json={
    "sourceFormat": "JsonSchema",
    "targetFormat": "OntologyRdf",
    "schema": "example schema here"
})

print("Converted schema:", r.json())
