from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from groupbuyorganizer import database
from groupbuyorganizer.admin.utilities import admin_check
from groupbuyorganizer.events.forms import CreateItemForm, CreateEventForm
from groupbuyorganizer.events.models import Event, Item


events = Blueprint('events', __name__)

@events.route('/events/<int:event_id>', methods=['GET', 'POST'])
@login_required
def event(event_id):
    event = Event.query.get_or_404(event_id)
    form = CreateItemForm()
    # if form.validate_on_submit():
    #     #todo query category
    #     item = Item()#todo
    #     database.session.add(item)
    #     database.session.commit()
    #     flash('Item successfully added!', 'success')
    #     return redirect(url_for(f'events.event/{event_id}'))
    return render_template('event.html', event=event, form=form, title=f'{event.name} Overview')


@events.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def event_edit(event_id):
    admin_check(current_user)
    event = Event.query.get_or_404(event_id)
    form = CreateEventForm()
    if form.validate_on_submit():
        event.name = form.event_name.data
        database.session.commit()
        flash(f'{event.name} has been edited!', 'info')
        return redirect(url_for('events.event_edit', event_id=event_id))
    elif request.method == 'GET':
        form.event_name.data = event.name
    return render_template('event_edit.html', title=f'{event.name} Edit', form=form, event=event)

@events.route("/category_settings/<int:category_id>/remove/", methods=['GET'])
@login_required
def category_remove(category_id):
    admin_check(current_user)
    event = Event.query.get_or_404(category_id)
    database.session.delete(event)
    database.session.commit()
    flash('Event deleted!', 'info')
    return redirect(url_for('event.category_settings'))