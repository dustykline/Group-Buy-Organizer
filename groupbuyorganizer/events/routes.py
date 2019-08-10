from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from groupbuyorganizer import database
from groupbuyorganizer.events.forms import CreateItemForm
from groupbuyorganizer.events.models import Event, Item

events = Blueprint('events', __name__)

@events.route('/events/<int:event_id>', methods=['GET', 'POST'])
@login_required
def event(event_id):
    event = Event.query.get_or_404(event_id)
    form = CreateItemForm
    # if form.validate_on_submit():
    #     #todo query category
    #     item = Item()#todo
    #     database.session.add(item)
    #     database.session.commit()
    #     flash('Item successfully added!', 'success')
    #     return redirect(url_for(f'events.event/{event_id}'))

    return render_template('event.html', event=event, form=form)