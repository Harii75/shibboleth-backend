from saml_backend import ServiceServer

if __name__ == "__main__":
    my_app_instance = ServiceServer()
    app = my_app_instance.app
    app.run(host="0.0.0.0", port=3000, ssl_context=("/app/kulcs.crt", "/app/kulcs.key"))
