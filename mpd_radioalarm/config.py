HTTP_PORT=8080
COOKIE_SECRET = "HELLO_WORLD"

ROOT_USER_EMAIL = 'root@localhost'
ROOT_USER_PASSWORD = 'password'

HASH_PASSWORD = True
HASH_ALGO='sha256'
HASH_SALT='sweet_salt'
HASH_ITERATIONS=100000

# Do not change
def get_resource_path(relative_path):
    return '../resources/' + relative_path

def get_userdata_path(relative_path):
    return '../user/' + relative_path

TEMPLATE_PATH = get_resource_path('html/templates')
STATIC_FILE_PATH = get_resource_path('html/static')
DATABASE_PATH = get_userdata_path('data/database.db')
