import base64
import time
import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect  # Added for route guarding redirects
from jwt.algorithms import RSAAlgorithm

User = get_user_model()

JWKS_CACHE = None
JWKS_CACHE_TIME = 0
JWKS_TTL = 3600  # Cache for 1 hour

def get_clerk_frontend_domain():
    # 1. Direct Hardcoded Fallback (Safest for your prototype)
    return "complete-pelican-54.clerk.accounts.dev"
    try:
        pk = getattr(settings, 'CLERK_PUBLISHABLE_KEY', None) or getattr(settings, 'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY', None)
        if not pk:
            return None
        parts = pk.split('_')
        if len(parts) >= 3:
            b64_part = parts[2].split('$')[0]
            b64_part += '=' * (4 - len(b64_part) % 4)
            domain = base64.b64decode(b64_part).decode('utf-8')
            return domain.strip().rstrip('$').replace('\x00', '')
    except Exception:
        return None
    return None

def get_clerk_jwks():
    global JWKS_CACHE, JWKS_CACHE_TIME
    now = time.time()
    
    if JWKS_CACHE is not None and (now - JWKS_CACHE_TIME) < JWKS_TTL:
        return JWKS_CACHE
        
    try:
        headers = {
            'Authorization': f'Bearer {settings.CLERK_SECRET_KEY}'
        }
        resp = requests.get('https://api.clerk.com/v1/jwks', headers=headers, timeout=5)
        resp.raise_for_status()
        JWKS_CACHE = resp.json()
        JWKS_CACHE_TIME = now
        return JWKS_CACHE
    except Exception as e:
        print(f"[Clerk Middleware] Authenticated JWKS fetch failed: {e}")

    domain = get_clerk_frontend_domain()
    if domain:
        try:
            resp = requests.get(f'https://{domain}/.well-known/jwks.json', timeout=5)
            resp.raise_for_status()
            JWKS_CACHE = resp.json()
            JWKS_CACHE_TIME = now
            return JWKS_CACHE
        except Exception as e:
            print(f"[Clerk Middleware] Public JWKS fallback fetch failed: {e}")

    return JWKS_CACHE or {}

def get_public_key(token):
    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception:
        return None

    kid = unverified_header.get('kid')
    if not kid:
        return None

    jwks = get_clerk_jwks()
    if not jwks or 'keys' not in jwks:
        return None

    for key_data in jwks['keys']:
        if key_data.get('kid') == kid:
            return RSAAlgorithm.from_jwk(key_data)

    return None

def verify_clerk_token(token):
    public_key = get_public_key(token)
    if not public_key:
        return None
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            options={"verify_aud": False}
        )
        return payload
    except Exception as e:
        print(f"[Clerk Middleware] Token verification failed: {e}")
        return None

def fetch_clerk_user_info(user_id):
    try:
        headers = {
            'Authorization': f'Bearer {settings.CLERK_SECRET_KEY}'
        }
        resp = requests.get(f'https://api.clerk.com/v1/users/{user_id}', headers=headers, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[Clerk Middleware] Failed to fetch Clerk profile metadata: {e}")
        return None

def get_or_create_clerk_user(clerk_id):
    user = User.objects.filter(username=clerk_id).first()
    if user:
        return user

    info = fetch_clerk_user_info(clerk_id)
    email = ""
    first_name = ""
    last_name = ""

    if info:
        first_name = info.get('first_name') or ""
        last_name = info.get('last_name') or ""
        emails = info.get('email_addresses') or []
        if emails:
            primary_email_id = info.get('primary_email_address_id')
            primary_email = next((e for e in emails if e.get('id') == primary_email_id), emails[0])
            email = primary_email.get('email_address') or ""

    if not email:
        email = f"{clerk_id}@clerk.placeholder"

    user = User.objects.create_user(
        username=clerk_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=User.Role.VOLUNTEER
    )
    return user

class ClerkAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 🚨 THE TOTAL ADMIN BYPASS 🚨
        # If the request is trying to go to the Django Admin backend, 
        # completely step out of the way and let native Django handle it!
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        # ... rest of your existing middleware code stays exactly the same ...
        token = request.COOKIES.get('__session')
        # ...

        # 1. TOKEN VERIFICATION LAYER
        clerk_user = None
        if token:
            payload = verify_clerk_token(token)
            if payload:
                clerk_id = payload.get('sub')
                if clerk_id:
                    clerk_user = get_or_create_clerk_user(clerk_id)

        # Assign the resolved user context to the request framework
        if clerk_user:
            request.user = clerk_user
        else:
            request.user = AnonymousUser()

        # 2. THE FINISH LINE LOOP-BREAKER
        # Look for the URL parameters we pass during redirects to let the frontend script run and drop cookies
        is_clerk_redirect = 'clerk' in request.GET or 'clerk_status' in request.GET or '__clerk_status' in request.GET
        
        # 3. ADVANCED ROUTE GUARD
        # Guarded volunteer-restricted applications spaces
        is_protected = any(request.path.startswith(prefix) for prefix in [
            '/dashboard/', 
            '/profile/card/', 
            '/certificates/download/',
            '/opportunities/',
            '/attendance/',
            '/opportunity/'
        ])
        
        # If the user is unauthenticated, trying to hit a protected path, and hasn't just come back from Clerk...
        if not clerk_user and is_protected and not is_clerk_redirect:
            return redirect('/?login=true')
        
        return self.get_response(request)