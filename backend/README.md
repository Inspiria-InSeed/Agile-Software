 # Agile-Software — Backend

## Environment Setup

1. Copy .env.example to .env:
   ```bash
   cp .env.example .env

   ```

## API Conventions

### Base URL

http://localhost:3000/api

### API Versioning

The initial API uses the /api prefix without a version number.
Future breaking changes may introduce versioned routes.

### Swagger Documentation

http://localhost:3000/api/docs

### Request Validation

- Unknown DTO properties are rejected.
- Invalid request parameters return HTTP 400.
- Request parameters are transformed into DTO types.

### Pagination

- page: Default 1, minimum 1.
- limit: Default 10, minimum 1, maximum 100.
- Responses contain data and meta.
- Metadata includes page, limit, total and totalPages.

### Filtering

The sample endpoint supports case-insensitive search.
Search text must not exceed 100 characters.
Filtering is applied before pagination.

### Error Response Format

All standardized error responses contain:

- success
- statusCode
- message
- error
- timestamp
- path

### CORS

Configure approved frontend origins using CORS_ORIGINS
in the backend environment.

Example:

```env
CORS_ORIGINS="http://localhost:5173"
```

Multiple origins can be separated by commas.
Unconfigured origins are not allowed cross-origin browser access.

### Sample Endpoint

GET /api/sample?page=1&limit=10&search=alpha

This endpoint demonstrates pagination, filtering and DTO
validation using temporary sample data without a database.

### Testing

```bash
npm run test
npm run test:e2e
```
