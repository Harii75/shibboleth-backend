import saml2
from saml2 import saml, xmldsig
import os

# Alapkönyvtár meghatározása (állítsd be a helyes útvonalat)
SERVER_BASEDIR = os.path.dirname(os.path.abspath(__file__))
PRIVATE_KEY_PATH = os.path.join(SERVER_BASEDIR, "app", "kulcs.key")
CERTIFICATE_PATH = os.path.join(SERVER_BASEDIR, "app", "kulcs.crt")

# SAML szerver konfiguráció
SERVER_CONFIG = {
    "entityid": 'https://192.168.101.60:3000/saml2/metadata/',  # Az entitás azonosító URL-je
    'metadata': {
        'remote': [{"url": "https://s3.eduid.hu/href-2020/sze.xml"}],  # Távoli metadata URL
    },
    'service': {
        'sp': {
            'name': 'Your Service Provider Name',  # Szolgáltató neve
            'name_id_format': "urn:oasis:names:tc:SAML:2.0:nameid-format:transient",
            'endpoints': {
                # ACS (Assertion Consumer Service) endpointok
                'assertion_consumer_service': [
                    ('https://192.168.101.60:3000/saml2/acs', saml2.BINDING_HTTP_REDIRECT),
                    ('https://192.168.101.60:3000/saml2/acs', saml2.BINDING_HTTP_POST),
                ],
                # Single Logout Service (SLO) endpoint
                'single_logout_service': [
                    ('https://192.168.101.60:3000/saml2/sls', saml2.BINDING_HTTP_REDIRECT),
                ],
            },
            'allow_unsolicited': True,  # Nem kívánt SAML üzenetek engedélyezése
            'authn_requests_signed': False,  # Hitelesítési kérések aláírása
            'logout_requests_signed': True,  # Kijelentkezési kérések aláírása
            'want_assertions_signed': False,  # Assertion-ok aláírásának követelése
            'want_response_signed': True,  # Válaszok aláírásának követelése
            'signing_algorithm': saml2.xmldsig.SIG_RSA_SHA256,  # Aláírás algoritmusa
            'digest_algorithm': saml2.xmldsig.DIGEST_SHA256,  # Kivonat algoritmusa
            'attribute_map_dir': None,  # Attribútum-térkép útvonala
        },
    },
    # Privát kulcs és tanúsítványok útvonala (állítsd be a megfelelő fájlokat)
    'key_file': os.path.join(SERVER_BASEDIR, 'app/kulcs.key'),
    'cert_file': os.path.join(SERVER_BASEDIR, 'app/kulcs.crt'),
    'encryption_keypairs': [{
        'key_file': os.path.join(SERVER_BASEDIR, 'app/kulcs.key'),  # Titkosító kulcs
        'cert_file': os.path.join(SERVER_BASEDIR, 'app/kulcs.crt'),  # Titkosító tanúsítvány
    }],
}
