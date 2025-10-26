# 🔐 EpiWatch Authentication API Documentation

## Overview

Complete authentication system with user registration, login, and token validation for the EpiWatch mobile application.

---

## 📋 Table of Contents

1. [Endpoints](#endpoints)
2. [Request/Response Schemas](#schemas)
3. [Authentication Flow](#flow)
4. [Error Handling](#errors)
5. [Security](#security)
6. [Testing](#testing)
7. [Android Integration](#android)

---

## 🔌 Endpoints

### Base URL
```
Production: https://epiwatch-api-qil4.onrender.com
Local: http://localhost:8000
```

---

### 1. User Registration (Signup)

**Endpoint:** `POST /api/v1/auth/signup`

**Description:** Register a new user account

**Request Body:**
```json
{
  "fullName": "John Doe",
  "email": "john.doe@example.com",
  "organization": "World Health Organization",
  "password": "securepassword123",
  "confirmPassword": "securepassword123"
}
```

**Success Response (201 Created):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "fullName": "John Doe",
    "email": "john.doe@example.com",
    "organization": "World Health Organization",
    "createdAt": "2025-10-26T12:34:56.789123"
  },
  "message": "Account created successfully! Welcome to EpiWatch."
}
```

**Error Responses:**
- **400 Bad Request:** Validation errors (missing fields, passwords don't match)
- **409 Conflict:** Email already registered
- **500 Server Error:** Internal server error

---

### 2. User Login

**Endpoint:** `POST /api/v1/auth/login`

**Description:** Authenticate user and get access token

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "securepassword123"
}
```

**Success Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "fullName": "John Doe",
    "email": "john.doe@example.com",
    "organization": "World Health Organization",
    "createdAt": "2025-10-26T12:34:56.789123"
  },
  "message": "Login successful! Welcome back to EpiWatch."
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid email or password
- **500 Server Error:** Internal server error

---

### 3. Token Validation

**Endpoint:** `GET /api/v1/auth/validate`

**Description:** Validate JWT token and get user information

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK):**
```json
{
  "valid": true,
  "user": {
    "id": 1,
    "fullName": "John Doe",
    "email": "john.doe@example.com",
    "organization": "World Health Organization",
    "createdAt": "2025-10-26T12:34:56.789123"
  }
}
```

**Invalid Token Response (200 OK):**
```json
{
  "valid": false,
  "user": null
}
```

---

## 📝 Request/Response Schemas

### SignUpRequest
```typescript
{
  fullName: string;        // Min 2 chars, Max 255 chars
  email: string;           // Valid email format
  organization?: string;   // Optional, Max 255 chars
  password: string;        // Min 6 chars
  confirmPassword: string; // Must match password
}
```

### LoginRequest
```typescript
{
  email: string;    // Valid email format
  password: string; // User's password
}
```

### UserResponse
```typescript
{
  id: number;
  fullName: string;
  email: string;
  organization: string | null;
  createdAt: string; // ISO 8601 format
}
```

### AuthResponse
```typescript
{
  token: string;      // JWT token
  user: UserResponse;
  message: string;    // Success message
}
```

### TokenValidationResponse
```typescript
{
  valid: boolean;
  user: UserResponse | null;
}
```

---

## 🔄 Authentication Flow

### Registration Flow
```
1. User submits signup form
2. Backend validates input (password match, email format)
3. Check if email already exists
4. Hash password with bcrypt
5. Create user in database
6. Generate JWT token (24h expiry)
7. Return token + user info
```

### Login Flow
```
1. User submits email + password
2. Find user by email
3. Verify password with bcrypt
4. Update last_login timestamp
5. Generate JWT token (24h expiry)
6. Return token + user info
```

### Token Validation Flow
```
1. Extract token from Authorization header
2. Decode JWT token
3. Verify signature and expiry
4. Find user in database
5. Return validation result + user info
```

---

## ❌ Error Handling

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful login or validation |
| 201 | Created | Successful registration |
| 400 | Bad Request | Validation errors, missing fields |
| 401 | Unauthorized | Invalid credentials or token |
| 409 | Conflict | Email already exists |
| 422 | Validation Error | Pydantic validation failed |
| 500 | Server Error | Internal server error |

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## 🔒 Security Features

### Password Security
- **Hashing Algorithm:** bcrypt
- **Minimum Length:** 6 characters
- **Storage:** Only hashed passwords stored (never plaintext)

### JWT Tokens
- **Algorithm:** HS256
- **Expiry:** 24 hours
- **Payload:** User email and ID
- **Secret:** Environment variable (SECRET_KEY)

### CORS Configuration
- **Allowed Origins:** `http://localhost:8081` (mobile app)
- **Credentials:** Enabled
- **Methods:** All
- **Headers:** All

### Database
- **Email:** Unique index for fast lookup
- **Timestamps:** Auto-generated created_at
- **Last Login:** Tracked for security monitoring

---

## 🧪 Testing

### Run Test Script

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start the API server
cd epiwatch
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, run tests
python test_auth_api.py
```

### Manual Testing with curl

**Signup:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "John Doe",
    "email": "john@example.com",
    "organization": "WHO",
    "password": "password123",
    "confirmPassword": "password123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

**Validate Token:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/validate \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📱 Android Integration

### Retrofit API Interface

```kotlin
// ApiService.kt
interface EpiWatchAuthApi {
    
    @POST("api/v1/auth/signup")
    suspend fun signup(
        @Body request: SignUpRequest
    ): Response<AuthResponse>
    
    @POST("api/v1/auth/login")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<AuthResponse>
    
    @GET("api/v1/auth/validate")
    suspend fun validateToken(
        @Header("Authorization") token: String
    ): Response<TokenValidationResponse>
}
```

### Data Classes

```kotlin
// Models.kt
data class SignUpRequest(
    val fullName: String,
    val email: String,
    val organization: String?,
    val password: String,
    val confirmPassword: String
)

data class LoginRequest(
    val email: String,
    val password: String
)

data class UserResponse(
    val id: Int,
    val fullName: String,
    val email: String,
    val organization: String?,
    val createdAt: String
)

data class AuthResponse(
    val token: String,
    val user: UserResponse,
    val message: String
)

data class TokenValidationResponse(
    val valid: Boolean,
    val user: UserResponse?
)
```

### Repository Implementation

```kotlin
// AuthRepository.kt
class AuthRepository(private val api: EpiWatchAuthApi) {
    
    suspend fun signup(
        fullName: String,
        email: String,
        organization: String?,
        password: String,
        confirmPassword: String
    ): Result<AuthResponse> {
        return try {
            val request = SignUpRequest(
                fullName, email, organization, 
                password, confirmPassword
            )
            val response = api.signup(request)
            
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.message()))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun login(
        email: String, 
        password: String
    ): Result<AuthResponse> {
        return try {
            val request = LoginRequest(email, password)
            val response = api.login(request)
            
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.message()))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun validateToken(token: String): Result<TokenValidationResponse> {
        return try {
            val response = api.validateToken("Bearer $token")
            
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.message()))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Token Storage (SharedPreferences)

```kotlin
// TokenManager.kt
class TokenManager(private val context: Context) {
    
    private val prefs = context.getSharedPreferences(
        "epiwatch_prefs", 
        Context.MODE_PRIVATE
    )
    
    fun saveToken(token: String) {
        prefs.edit().putString("auth_token", token).apply()
    }
    
    fun getToken(): String? {
        return prefs.getString("auth_token", null)
    }
    
    fun clearToken() {
        prefs.edit().remove("auth_token").apply()
    }
    
    fun isLoggedIn(): Boolean {
        return getToken() != null
    }
}
```

### Retrofit Setup with Token Interceptor

```kotlin
// NetworkModule.kt
class AuthInterceptor(private val tokenManager: TokenManager) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val request = chain.request()
        val token = tokenManager.getToken()
        
        val newRequest = if (token != null) {
            request.newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        } else {
            request
        }
        
        return chain.proceed(newRequest)
    }
}

val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(AuthInterceptor(tokenManager))
    .build()

val retrofit = Retrofit.Builder()
    .baseUrl("https://epiwatch-api-qil4.onrender.com/")
    .client(okHttpClient)
    .addConverterFactory(GsonConverterFactory.create())
    .build()
```

---

## 📦 File Structure

```
backend/
├── main.py                 # FastAPI app with routes included
├── models.py               # SQLAlchemy User model
├── schemas.py              # Pydantic request/response schemas
├── database.py             # Database configuration
├── auth_utils.py           # Password hashing & JWT functions
├── auth_routes.py          # Authentication endpoints
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
└── epiwatch.db            # SQLite database (auto-created)
```

---

## 🚀 Deployment Notes

### Environment Variables

Create a `.env` file in the backend directory:

```bash
SECRET_KEY=your-super-secret-key-here-change-this
DATABASE_URL=sqlite:///./epiwatch.db
CORS_ORIGINS=http://localhost:8081,https://your-mobile-app.com
```

### Generate Secure SECRET_KEY

```bash
# Using OpenSSL
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database Migration (Production)

For production, consider using PostgreSQL instead of SQLite:

```python
# In database.py
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./epiwatch.db")
```

---

## ✅ Implementation Checklist

- [x] User model with SQLAlchemy
- [x] Password hashing with bcrypt
- [x] JWT token generation and validation
- [x] Signup endpoint with validation
- [x] Login endpoint with authentication
- [x] Token validation endpoint
- [x] Error handling (400, 401, 409, 500)
- [x] CORS configuration for mobile app
- [x] Database initialization
- [x] Test script
- [x] Documentation
- [x] Android integration examples

---

## 📞 Support

For issues or questions:
- API Docs: https://epiwatch-api-qil4.onrender.com/api/docs
- GitHub: https://github.com/yashwith9/epiwatch_api

---

**Version:** 1.0.0  
**Last Updated:** October 26, 2025  
**Status:** ✅ Production Ready
