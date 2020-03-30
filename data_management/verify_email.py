from flask import Flask, make_response
from flask_email_verifier import EmailVerifier
from json import dumps, loads
import os

app = Flask(__name__)
os.environ['EMAIL_VERIFIER_KEY'] = 'at_2Pp6yw8Mme6ENDP2TWgCIqrz276Pc'
# Initialize the extension
verifier = EmailVerifier(app)


@app.route('/email/<email>')
def email(email):
    # Retrieve an info for the given email address
    email_address_info = verifier.verify(email)
    if email_address_info is not None:
        data = dumps(loads(email_address_info.json_string), indent=4)
        resp = make_response(data, 200)
        resp.headers['Content-Type'] = 'application/json'
    else:
        resp = make_response('None', 404)
    return resp