import datetime
import os

from saml2 import saml
import saml2
from saml2.client import Saml2Client
from saml2.config import SPConfig
from saml2.metadata import entity_descriptor
from saml2 import config
from flask import Flask, Response, redirect, request, jsonify
import jwt
from lxml import etree
from flask_cors import CORS  # Import CORS for frontend compatibility

# Import configuration and private key path
from saml_config import SERVER_CONFIG, PRIVATE_KEY_PATH

# Set XMLSEC_BINARY path explicitly
os.environ["XMLSEC_BINARY"] = "/usr/bin/xmlsec1"  # Adjust path if necessary


class ServiceServer:
    def __init__(self):
        # Load the private key
        with open(PRIVATE_KEY_PATH, 'r') as key_file:
            self.PRIVATE_KEY = key_file.read()

        # Initialize Flask app with CORS enabled for frontend
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/*": {"origins": "http://localhost:5173"}})

        # Initialize SAML2 client
        self.saml_client = self.initialize_saml_client()

        # Add authentication routes
        self.add_routes()

    def initialize_saml_client(self):
        """Initialize and configure the SAML2 client."""
        conf = config.SPConfig()
        conf.load(SERVER_CONFIG)
        return Saml2Client(config=conf)

    def add_routes(self):
        """Define all routes for authentication."""

        @self.app.route('/saml2/metadata/')
        def saml_metadata():
            """Generate and return the SAML metadata XML."""
            sp_config = SPConfig()
            sp_config.load(SERVER_CONFIG)
            metadata = entity_descriptor(sp_config)
            return Response(metadata.to_string(), content_type='application/xml')

        @self.app.route('/saml2/acs/', methods=['POST'])
        def acs():
            """Handle the Assertion Consumer Service (ACS) for processing SAML responses."""
            saml_response = request.form.get('SAMLResponse')

            # Process SAML response
            authn_response = self.saml_client.parse_authn_request_response(
                saml_response,
                binding='urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
            )

            if authn_response is not None and authn_response.ava:
                user_info = authn_response.ava  # Extract user attributes
                tree = etree.fromstring(authn_response.xmlstr)
                attributes = tree.findall(".//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute")

                # Look for niifPersonOrgID
                niif_person_org_id = None
                for attr in attributes:
                    if attr.attrib.get('FriendlyName') == 'niifPersonOrgID':
                        _niif_person_org_id = attr.findtext(".//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
                        niif_person_org_id = _niif_person_org_id
                if niif_person_org_id is not None:
                    user_info['niifPersonOrgID'] = niif_person_org_id

                # Generate JWT token
                token = jwt.encode({
                    'sub': user_info,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                }, self.PRIVATE_KEY, algorithm='RS256')

                # Return JSON response instead of redirect
                response = jsonify({"token": token})
                response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
                response.headers.add("Access-Control-Allow-Credentials", "true")
                return response

            return jsonify({"error": "Authentication failed"}), 401

        @self.app.route('/login')
        def login():
            """Initiate SAML authentication and redirect user to IdP."""
            binding, authn_request = self.saml_client.prepare_for_authenticate()

            # Find the redirect location
            for header, value in authn_request['headers']:
                if header == 'Location':
                    return jsonify({"redirect_url": value})

            return jsonify({"error": "No Location header found"}), 400