from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    return render_template('404.html', title='404'), 404

@errors.app_errorhandler(500)
def error_404(error):
    return render_template('500.html', title='500'), 500