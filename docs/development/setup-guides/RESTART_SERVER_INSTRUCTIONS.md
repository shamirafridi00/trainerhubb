# Server Restart Instructions

## Why Restart?

New endpoints added in Epic 0.2 need the Django server to be restarted to become available:
- `/api/admin/trainers/bulk-action/`
- `/api/admin/trainers/export/`
- `/api/admin/trainers/{id}/export-detail/`
- `/api/admin/dashboard/export-stats/`

---

## How to Restart

### Option 1: Using Terminal 4 (Where Server is Running)

1. **Find Terminal 4** (where server is currently running)
2. **Stop the server:**
   - Press `Ctrl+C`
3. **Start the server again:**
   ```bash
   cd /home/shamir/trainerhubb
   source venv/bin/activate
   python manage.py runserver 0.0.0.0:8000
   ```

---

### Option 2: Kill and Restart

```bash
# Find the process
ps aux | grep "manage.py runserver"

# Kill it (replace PID with actual process ID)
kill PID

# Start fresh
cd /home/shamir/trainerhubb
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

---

## Verify Server is Running

```bash
curl http://localhost:8000/api/admin/trainers/ \
  -H "Authorization: Token 546c1efad11fef08bb6d0ea17fe84513f59e9431"
```

Should return JSON with trainer list.

---

## Test New Endpoints

After restart, test the new features:

### 1. Test Export
```bash
TOKEN="546c1efad11fef08bb6d0ea17fe84513f59e9431"
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/admin/trainers/export/ \
  -o trainers_test.csv

# Check the file
cat trainers_test.csv
```

### 2. Test Bulk Action
```bash
curl -X POST http://localhost:8000/api/admin/trainers/bulk-action/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"verify","trainer_ids":[2,3]}'
```

---

## Expected Output

### Server Starting:
```
System check identified no issues (0 silenced).
December 29, 2024 - 12:00:00
Django version 5.x.x, using settings 'config.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### Export Test:
```
ID,Business Name,Email,User Active,Is Verified,...
3,Shamir Afridi,shamirafridi24@gmail.com,Yes,No,...
2,Test Fitness Studio,test_trainer@trainerhub.com,Yes,No,...
```

### Bulk Action Test:
```json
{
  "action": "verify",
  "success_count": 2,
  "failed_count": 0,
  "failed": [],
  "message": "Successfully verifyed 2 trainer(s)"
}
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 PID
```

### Server Won't Start
```bash
# Check for errors
python manage.py check

# Run migrations if needed
python manage.py migrate
```

### Still Getting 404
- Make sure you restarted the server
- Check the URL is correct (note the underscore: `bulk-action` not `bulk_action`)
- Verify token is valid

---

## Quick Test Command

Run this after restart to test everything:

```bash
TOKEN="546c1efad11fef08bb6d0ea17fe84513f59e9431"

echo "Testing export..."
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/admin/trainers/export/ \
  -o /tmp/test_export.csv && echo "✓ Export works!" || echo "✗ Export failed"

echo "Testing bulk action..."
curl -X POST http://localhost:8000/api/admin/trainers/bulk-action/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"verify","trainer_ids":[]}' \
  && echo "✓ Bulk action endpoint available!" || echo "✗ Bulk action failed"
```

---

**Once restarted, all Epic 0.2 features will be available!**

