from flask import Blueprint
drst = Blueprint('drst', __name__,
                        template_folder = 'templates',
                        static_url_path = '/static',
                        static_folder = 'static')
