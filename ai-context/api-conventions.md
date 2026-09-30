This document contains references to Cornerstone

# API Conventions

Cornerstone uses REST.

Success responses should use:

```json
{
  "data": {},
  "meta": {}
}
```

Error responses should use:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message.",
    "details": []
  }
}
```

Required baseline endpoints:

GET /health
GET /ready
GET /version

Authentication should be verified in the API layer. Application authorization should be enforced in service logic.
