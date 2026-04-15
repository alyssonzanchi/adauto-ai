# Vehicle CRUD - Quick Testing Guide

## Backend Testing

### 1. Start Services
```bash
cd docker
docker-compose up -d postgres redis minio
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
alembic upgrade head
```

### 4. Start Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test Endpoints (using curl or Postman)

#### Create Vehicle
```bash
curl -X POST "http://localhost:8000/api/v1/vehicles" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Honda Civic Touring 2023",
    "description": "Hondas Civic Touring impecável, único dono",
    "brand": "Honda",
    "model": "Civic",
    "year": 2023,
    "model_year": 2023,
    "version": "Touring",
    "color": "Branco Pérola",
    "mileage": 15000,
    "plate": "ABC1234",
    "chassis": "93H123456789",
    "doors": 4,
    "seats": 5,
    "fuel_type": "flex",
    "transmission": "automatic",
    "body_type": "sedan",
    "price": 125000.00,
    "features": {
      "security": ["airbags", "abs", "controle_estabilidade"],
      "comfort": ["ar_condicionado", "direcao_eletrica", "bancos_couro"],
      "technology": ["central_multimidia", "gps", "android_auto"]
    },
    "status": "pending"
  }'
```

#### List Vehicles
```bash
curl -X GET "http://localhost:8000/api/v1/vehicles?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Filter Vehicles
```bash
curl -X GET "http://localhost:8000/api/v1/vehicles?brand=Honda&year_min=2020&status=active" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Single Vehicle
```bash
curl -X GET "http://localhost:8000/api/v1/vehicles/{vehicle_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Update Vehicle
```bash
curl -X PUT "http://localhost:8000/api/v1/vehicles/{vehicle_id}" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 120000.00,
    "status": "active"
  }'
```

#### Analyze Vehicle (AI)
```bash
curl -X POST "http://localhost:8000/api/v1/vehicles/{vehicle_id}/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Upload Images
```bash
curl -X POST "http://localhost:8000/api/v1/vehicles/{vehicle_id}/images?set_main=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@/path/to/image1.jpg" \
  -F "files=@/path/to/image2.jpg"
```

#### Delete Image
```bash
curl -X DELETE "http://localhost:8000/api/v1/vehicles/{vehicle_id}/images/0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Set Main Image
```bash
curl -X PATCH "http://localhost:8000/api/v1/vehicles/{vehicle_id}/images/1/set-main" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Delete Vehicle
```bash
curl -X DELETE "http://localhost:8000/api/v1/vehicles/{vehicle_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Frontend Testing

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

### 3. Open Browser
```
http://localhost:3000/vehicles
```

### 4. Test Features
- Search vehicles
- Filter by brand, status, price range
- Pagination
- View vehicle details
- Check price position indicators
- View vehicle images

## MinIO Console

### Access Console
```
URL: http://localhost:9001
Username: minioadmin
Password: minioadmin
```

### Verify Images
1. Login to console
2. Open bucket "car-ads-images"
3. Navigate to "vehicles/{vehicle_id}/"
4. Verify uploaded images

## Validation Tests

### Vehicle Validations
- [ ] Title min 5 characters
- [ ] Brand and model min 2 characters
- [ ] Year between 1900 and 2030
- [ ] model_year >= year and <= year+1
- [ ] Price > 0
- [ ] Chassis unique (if provided)

### Image Validations
- [ ] Max 10MB per file
- [ ] Only jpg, png, webp formats
- [ ] Max 20 images per vehicle
- [ ] Automatic resize to max 1200px width
- [ ] JPEG 85% quality compression

### Permission Tests
- [ ] USER role: can only view
- [ ] MANAGER role: can create/edit own dealership vehicles
- [ ] ADMIN role: can do everything

## Common Issues

### Issue: "Chassis already registered"
**Solution**: Use a different chassis number or check if vehicle exists

### Issue: "Maximum 20 images per vehicle"
**Solution**: Delete some images before uploading more

### Issue: "Invalid file type"
**Solution**: Only jpg, jpeg, png, and webp are supported

### Issue: MinIO connection error
**Solution**: Ensure MinIO is running: `docker-compose up -d minio`

### Issue: Images not displaying
**Solution**: Check MinIO console and verify bucket policy allows public access

## Performance Checks

### Response Times
- List vehicles: < 200ms
- Get single vehicle: < 100ms
- Upload image: < 2s (per image)
- AI analysis: < 1s

### Pagination
- Default page size: 20
- Max page size: 100
- Check total pages in response

## Database Verification

### Check Vehicles Table
```sql
SELECT id, title, brand, model, year, price, status
FROM vehicles
WHERE deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 10;
```

### Check Image Count
```sql
SELECT id, title, array_length(images, 1) as image_count
FROM vehicles
WHERE deleted_at IS NULL
ORDER BY created_at DESC;
```

### Check AI Analysis
```sql
SELECT id, title, price, price_market, price_score, price_position
FROM vehicles
WHERE deleted_at IS NULL AND ai_analysis IS NOT NULL
ORDER BY created_at DESC;
```

## Next Steps

After testing is complete:
1. ✅ All endpoints working
2. ✅ Image upload functional
3. ✅ Frontend displaying vehicles
4. ✅ Filters and pagination working
5. ✅ AI analysis returning results (mock)

Proceed to **Week 5: AI Implementation**
- Replace mock AI with real Claude API
- Implement advanced pricing models
- Add ML predictions
