from flask import flask, request, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

mail = Mail(app)

s = URLSafeTimedSerializer('randomkey')

@app.route('/', methods=['GET', 'POST'])
def index():
    ## allow email to be submitted

    ## get the email from the page
    email = request.form['email']
    token = s.dumps(email)

    msg = Message('Confirm Email', sender= 'tigerpair@gmail.com', recipients=[email])

    link = url_for('confirm_email', token=token, _external=True)

    msg.body= 'Confirmation link is {}'.format(link)

    mail.send(msg)


@app.route('/confirm_email/<token>')
def confirm_email(token):

    try:
        email = s.loads(token, max_age=3600) #one hour to confirm
    except SignatureExpired:
        return 'The token is expired'

    # in the database we should have a confirmed email = false. When
    # we get here we should make confirmed = True

if __name__ == '__main__':
    app.run(debug=True)
