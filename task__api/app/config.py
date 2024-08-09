import os
import urllib.parse

original_url = os.getenv('DATABASE_URL')
if original_url:
    parsed = urllib.parse.urlparse(original_url)
    formatted_url = urllib.parse.urlunparse(parsed._replace(netloc=urllib.parse.quote(parsed.username) + ':' + urllib.parse.quote(parsed.password) + '@' + parsed.hostname + (':' + str(parsed.port) if parsed.port else '')))
    app.config['SQLALCHEMY_DATABASE_URI'] = formatted_url.replace("mysql://", "mysql+pymysql://", 1)
