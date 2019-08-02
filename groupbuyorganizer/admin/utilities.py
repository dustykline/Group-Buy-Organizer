from flask import flash, redirect, url_for
from flask_login import current_user

def admin_check(user):
    '''This protects against logged in users from accessing the admin pages, even if they know the direct URL.'''

    if user.is_admin == False:
        flash('Access denied.', 'danger')
        return redirect(url_for('general.home'))


def admin_protector(user):
    '''This function protects against those with admin power from manually inputting valid route commands to user
    functions, even when the buttons are disabled.
    '''

    if user.is_admin and current_user.is_admin and current_user.is_root == False:
        flash('Access denied.', 'danger')