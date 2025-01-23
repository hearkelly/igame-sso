# from iGame import cache
from authlib.jose import JsonWebToken
import requests
"""
https://docs.authlib.org/en/latest/jose/jwt.html#jwt-payload-claims-validation
REF - authlib
https://github.com/authlib/demo-oauth-client/
REF - Vuka
https://www.youtube.com/watch?v=BfYsdNaHrps
https://github.com/Vuka951/tutorial-code/tree/master/flask-google-oauth2

https://www.youtube.com/watch?v=wctDfjx4xIw
https://developers.google.com/identity/protocols/oauth2/web-server#python
https://www.youtube.com/watch?v=fZLWO3_V06Q
https://developers.google.com/identity/openid-connect/openid-connect#python
https://www.youtube.com/watch?v=FKgJEfrhU1E
"""
#@cache.memoize(timeout=2592000) # 1 month caching of google jwt keys
# error with caching:
# redis.exceptions.ConnectionError: Error 1 connecting to ec2-3-220-59-62.compute-1.amazonaws.com:16710.
# [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1007).
def get_google_jwks():
    try:
        rq = "https://www.googleapis.com/oauth2/v3/certs"  # google key uri
        response = requests.get(rq)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(e)
        return None

def get_jwt_claims(client_id:str, token:str, claims=None):  # decode, validate, and return
    keys = get_google_jwks()
    if keys:
        try:
            jwt_processor = JsonWebToken(['RS256'])
            claims = jwt_processor.decode(token, key=keys, claims_options={
                'iss': {'values':['accounts.google.com']},
                'aud': {'values': [client_id]}
            })
        except:
            return claims
        # validate the issuer and audience
        try:
            claims.validate_iss()
            claims.validate_aud()
        except:
            return None
    return claims


def get_email_from_claims(claims) -> str:
    if claims:
        try:
            return claims['email']
        except:
            raise KeyError

