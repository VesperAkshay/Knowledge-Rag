# Multi-User Authentication System

## Overview

The RAG Knowledge Base now supports multiple users with isolated data and user-specific credentials. Each user has their own:

- Unique user ID and session
- Personal API credentials (Google Gemini + ChromaDB)
- Isolated knowledge base collection
- Private chat history
- Separate document uploads

## Database Schema

### SQLite Database: `backend/database/rag_users.db`

**Tables:**

1. **users**
   - `id` (INTEGER PRIMARY KEY)
   - `user_id` (TEXT UNIQUE) - Format: `user_{random_token}`
   - `username` (TEXT UNIQUE)
   - `password_hash` (TEXT) - SHA-256 hashed
   - `created_at` (TEXT)
   - `last_login` (TEXT)

2. **user_credentials**
   - `user_id` (TEXT PRIMARY KEY, FK to users)
   - `google_api_key` (TEXT) - For Gemini API
   - `chromadb_api_key` (TEXT) - For ChromaDB Cloud
   - `chromadb_tenant` (TEXT) - ChromaDB tenant name
   - `chromadb_database` (TEXT) - ChromaDB database name

3. **sessions**
   - `session_id` (TEXT PRIMARY KEY) - Format: `session_{random_token}`
   - `user_id` (TEXT, FK to users)
   - `created_at` (TEXT)
   - `expires_at` (TEXT) - 24-hour expiry
   - `is_active` (BOOLEAN)

4. **chat_history**
   - `id` (INTEGER PRIMARY KEY)
   - `user_id` (TEXT, FK to users)
   - `message_id` (TEXT UNIQUE)
   - `role` (TEXT) - 'user' or 'assistant'
   - `content` (TEXT)
   - `timestamp` (TEXT)

## Authentication Flow

### 1. User Registration

**Endpoint:** `POST /api/auth/register`

**Request:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "user_id": "user_abc123xyz",
  "username": "john_doe",
  "message": "User registered successfully"
}
```

**Validation:**
- Username: Minimum 3 characters, unique
- Password: Minimum 6 characters
- Password is hashed with SHA-256 before storage

### 2. User Login

**Endpoint:** `POST /api/auth/login`

**Request:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "user_id": "user_abc123xyz",
  "username": "john_doe",
  "session_id": "session_def456uvw",
  "message": "Login successful"
}
```

**Session Cookie:**
- Name: `session_id`
- HTTP-only: Yes
- Expiry: 24 hours
- SameSite: Lax
- Secure: True (in production)

### 3. Get Current User

**Endpoint:** `GET /api/auth/me`

**Headers:**
- Cookie: `session_id=session_def456uvw`

**Response:**
```json
{
  "user_id": "user_abc123xyz",
  "username": "john_doe"
}
```

### 4. Save API Credentials

**Endpoint:** `POST /api/auth/credentials`

**Request:**
```json
{
  "google_api_key": "AIza...",
  "chromadb_api_key": "chroma_abc...",
  "chromadb_tenant": "my_tenant",
  "chromadb_database": "my_database"
}
```

**Response:**
```json
{
  "message": "Credentials saved successfully"
}
```

### 5. Get Saved Credentials

**Endpoint:** `GET /api/auth/credentials`

**Response:**
```json
{
  "google_api_key": "AIza****xyz",
  "chromadb_api_key": "chro****123",
  "chromadb_tenant": "my_tenant",
  "chromadb_database": "my_database"
}
```

**Note:** API keys are masked (first 4 + last 4 characters shown)

### 6. Logout

**Endpoint:** `POST /api/auth/logout`

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

## Protected Endpoints

All main API endpoints now require authentication and saved credentials:

### Chat Endpoint
**Endpoint:** `POST /api/chat`
- Requires: Valid session + Saved credentials
- Uses: User-specific Google API key and ChromaDB collection
- Saves: Messages to user's chat history

### Upload Endpoints
**Endpoints:**
- `POST /api/upload-file`
- `POST /api/upload-url`

- Requires: Valid session + Saved credentials
- Stores: Documents in user-specific ChromaDB collection
- Format: Collection name = `{user_id}_unified_knowledge_base`

### Knowledge Base Info
**Endpoint:** `GET /api/info` or `GET /api/knowledge-base-info`
- Requires: Valid session + Saved credentials
- Returns: Document count from user's collection

### Chat History
**Endpoints:**
- `GET /api/chat/history?limit=50` - Get chat history
- `DELETE /api/chat/history` - Clear chat history

- Requires: Valid session
- Returns: User's personal chat messages

## Middleware

### `require_auth(session_id: str)`
- Validates session ID from cookie
- Checks session expiry
- Returns user_id if valid
- Raises 401 if invalid/expired

### `require_credentials(session_id: str)`
- Calls `require_auth` first
- Checks if user has saved credentials
- Returns dict with user_id + all credentials
- Raises 403 if credentials not configured

## Security Features

1. **Password Hashing**
   - SHA-256 algorithm
   - No plain-text passwords stored

2. **Session Security**
   - HTTP-only cookies (not accessible via JavaScript)
   - 24-hour expiry
   - Secure flag in production
   - SameSite protection against CSRF

3. **Data Isolation**
   - Each user has unique ChromaDB collection
   - Chat history filtered by user_id
   - File uploads in user-specific directories (`uploads/{user_id}/`)

4. **Credential Masking**
   - API keys masked in GET responses
   - Only first/last 4 characters shown
   - Full keys never returned to frontend

## User-Specific Collections

### ChromaDB Collection Naming
Format: `{user_id}_unified_knowledge_base`

Example: `user_abc123xyz_unified_knowledge_base`

### Advantages
- Complete data isolation between users
- Each user can have different ChromaDB tenants/databases
- No risk of cross-user data access
- Easy to export/delete user data

## Frontend Integration (To Be Implemented)

### Required Pages

1. **Login Page** (`/login`)
   - Username/password form
   - Store session cookie on success
   - Redirect to main app

2. **Registration Page** (`/register`)
   - Username/password form with validation
   - Auto-login after registration

3. **Settings/Credentials Page** (`/settings`)
   - Form for API credentials:
     - Google Gemini API Key
     - ChromaDB API Key
     - ChromaDB Tenant
     - ChromaDB Database
   - Show masked current values
   - Update button

4. **Protected Main App** (`/`)
   - Check for valid session on mount
   - Redirect to login if not authenticated
   - Redirect to settings if credentials not configured
   - Load chat history on mount

### Auth Context (Recommended)

```typescript
// lib/contexts/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  hasCredentials: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  saveCredentials: (creds: Credentials) => Promise<void>;
}
```

## Testing

### Manual Testing Steps

1. **Register New User**
   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "test123"}'
   ```

2. **Login**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "test123"}' \
     -c cookies.txt
   ```

3. **Save Credentials**
   ```bash
   curl -X POST http://localhost:8000/api/auth/credentials \
     -H "Content-Type: application/json" \
     -b cookies.txt \
     -d '{
       "google_api_key": "your_key",
       "chromadb_api_key": "your_key",
       "chromadb_tenant": "your_tenant",
       "chromadb_database": "your_db"
     }'
   ```

4. **Test Chat**
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -b cookies.txt \
     -d '{"message": "What is machine learning?"}'
   ```

5. **Get Chat History**
   ```bash
   curl -X GET http://localhost:8000/api/chat/history \
     -b cookies.txt
   ```

## Environment Variables

No changes needed! User-specific credentials are stored in the database.

Optional: Set fallback/default credentials in `.env` for development:
```env
GOOGLE_API_KEY=your_dev_key
CHROMADB_API_KEY=your_dev_key
CHROMADB_TENANT=your_dev_tenant
CHROMADB_DATABASE=your_dev_database
```

## Database Management

### Initialize Database
Database auto-initializes on first import of `backend/database/db.py`

### Backup Database
```bash
cp backend/database/rag_users.db backend/database/rag_users.backup.db
```

### View Database
```bash
sqlite3 backend/database/rag_users.db
.tables
SELECT * FROM users;
```

### Reset Database (Caution!)
```bash
rm backend/database/rag_users.db
# Will recreate on next server start
```

## Session Cleanup

### Manual Cleanup (Remove expired sessions)
```python
from backend.database.db import SessionDB
SessionDB.cleanup_expired_sessions()
```

### Recommended: Add Scheduled Task
Create a background task to run cleanup every hour:

```python
# In app.py
from apscheduler.schedulers.background import BackgroundScheduler
from backend.database.db import SessionDB

scheduler = BackgroundScheduler()
scheduler.add_job(
    SessionDB.cleanup_expired_sessions,
    'interval',
    hours=1
)
scheduler.start()
```

## Production Deployment

### Security Checklist

- [ ] Use HTTPS (set `Secure=True` on cookies)
- [ ] Use strong secret key for session tokens
- [ ] Set proper CORS origins
- [ ] Enable rate limiting on auth endpoints
- [ ] Use environment variables for sensitive config
- [ ] Backup database regularly
- [ ] Monitor failed login attempts
- [ ] Implement password reset functionality
- [ ] Add email verification (optional)
- [ ] Use stronger password hashing (bcrypt/argon2)

### Scaling Considerations

- SQLite works well for small-to-medium deployments
- For larger scale, migrate to PostgreSQL/MySQL
- Consider Redis for session storage (faster)
- Implement connection pooling for ChromaDB
- Add caching layer for frequently accessed data

## Troubleshooting

### "401 Unauthorized" Error
- Session cookie missing or expired
- Login again to get new session

### "403 Forbidden - No credentials configured"
- User hasn't saved API credentials
- Go to settings page and configure credentials

### "Collection not found" Error
- User's ChromaDB collection doesn't exist yet
- Upload a document first to create collection

### Session expires too quickly
- Current: 24-hour expiry
- Modify in `backend/database/db.py`: Change `timedelta(hours=24)`

## Next Steps

1. ✅ Backend authentication complete
2. ⏳ Create frontend login/register pages
3. ⏳ Create settings page for credentials
4. ⏳ Add auth context provider
5. ⏳ Integrate with existing chat UI
6. ⏳ Load chat history on mount
7. ⏳ Add session refresh mechanism
8. ⏳ Implement password reset flow
9. ⏳ Add user profile management
10. ⏳ Production deployment

---

**Status:** Backend authentication system fully implemented and ready for frontend integration.
