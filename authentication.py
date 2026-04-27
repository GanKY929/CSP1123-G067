from flask import Flask, redirect, url_for, session, request
import msal, config

app = Flask(__name__)
app.secret_key = "super-secret-key"


CLIENT_ID = config.Client_ID
CLIENT_SECRET = config.Client_Secret
TENANT_ID = config.Tenant_ID
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_PATH = "/getAToken"
SCOPE = ["User.Read"]
redirect_uri = "http://localhost:5000" + REDIRECT_PATH


msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

def MSindex():
    if "user" in session:
        return f"Hello {session['user']['name']}! <a href='/logout'>Logout</a>"
    return "<a href='/login'>Login with Microsoft</a>"

def login():
    auth_url = msal_app.get_authorization_request_url(
        SCOPE,
        redirect_uri=redirect_uri
    )
    return redirect(auth_url)

def auth_callback():
    code = request.args.get("code")
    if not code:
        return "No authorization code returned", 400

    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=SCOPE,
        redirect_uri=redirect_uri
    )

    if "error" in result:
        return f"""
        Error: {result['error']}<br>
        Description: {result.get('error_description')}<br>
        Correlation ID: {result.get('correlation_id')}
        """, 401

    if "id_token_claims" in result:
        claims = result["id_token_claims"]
        session["user"] = claims
        session["access_token"] = result.get("access_token")
        return redirect(url_for("MSindex"))

    return "Authentication failed: no id_token_claims", 401

def logout():
    session.clear()
    logout_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/logout?post_logout_redirect_uri=http://localhost:5000"
    return redirect(logout_url)

# Register routes
app.add_url_rule("/", "MSindex", MSindex)
app.add_url_rule("/login", "login", login)
app.add_url_rule(REDIRECT_PATH, "auth_callback", auth_callback)
app.add_url_rule("/logout", "logout", logout)

if __name__ == "__main__":
    app.run(debug=True)

"""
Can't log in with Microsoft account yet. Will work on Microsoft login later.

As it will display this message when trying to log in with Microsoft account:

Need admin approval
MMUinfo
unverified
MMUinfo needs permission to access resources in your organisation that only an admin can grant. 
Please ask an admin to grant permission to this app before you can use it.

"""