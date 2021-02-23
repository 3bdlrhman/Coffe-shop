import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from werkzeug.datastructures import Headers


AUTH0_DOMAIN = 'localcompany.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'drink'


'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# get the header from the request, split it and return the token
def get_token_auth_header():
    data = request.headers.get('Authorization', None)
    if data is None:
        raise AuthError({
                'what happened': 'No header is present.'
            }, 401)
    auth_header = data.split()
    if auth_header[0].lower() != 'bearer' or len(auth_header) != 2:
        raise AuthError({
                'what happened': 'Authorization headers is malformed'
            }, 401)
    token = auth_header[1]
    return token


# checks the permission ('post:drink') if not included in the payload
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
                'what happened': 'Required Permission is NOT in the payload'
            }, 401)
    if permission not in payload['permissions']:
        raise AuthError({
                'what happened': 'This permission is not allowed'
            }, 401)
    return True


'''
    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload
'''
def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

'''
    use the get_token_auth_header method to get the token
    use the verify_decode_jwt method to decode the jwt
    use the check_permissions method validate claims and check the permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator


'''
https://localcompany.eu.auth0.com/authorize?audience=drink&response_type=token&client_id=jh0iQcsluYZp5ax0gNml8K0aB3sudrAq&redirect_uri=https://127.0.0.1:5000/login-results

'''