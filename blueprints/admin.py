# -*- coding: utf-8 -*-

__all__ = ()

import bcrypt
import datetime
import hashlib

import timeago
from functools import wraps
from quart import Blueprint
from quart import redirect
from quart import render_template
from quart import request
from quart import session

from objects import glob
from objects import db_utils
from objects import utils
from objects.privileges import Privileges
from objects.utils import flash

admin = Blueprint('admin', __name__)

def dict_cmp(a: dict, b: dict):
    cmp = a.items() - b.items()
    return dict(cmp)
    
def priv_check(priv: Privileges):
    def decorate(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not "authenticated" in session:
                return await flash('error', 'Por favor, inicie sesión primero.', 'login')

            if not session["user_data"]["priv"] & priv:
                return await flash('error', f'No tiene suficientes privilegios.', 'home')
            return await func(*args, **kwargs)

        return wrapper

    return decorate

@admin.route('/')
@admin.route('/home')
@admin.route('/dashboard')
@priv_check(priv=Privileges.Staff)
async def home():
    """Render the homepage of guweb's admin panel."""
    # fetch data from database
    dash_data = await glob.db.fetch(
        'SELECT COUNT(id) count, '
        '(SELECT name FROM users ORDER BY id DESC LIMIT 1) lastest_user, '
        '(SELECT COUNT(id) FROM users WHERE NOT priv & 1) banned '
        'FROM users'
    )

    recent_users = await glob.db.fetchall('SELECT * FROM users ORDER BY id DESC LIMIT 5')
    recent_scores = await glob.db.fetchall(
        'SELECT scores.*, maps.artist, maps.title, '
        'maps.set_id, maps.creator, maps.version '
        'FROM scores JOIN maps ON scores.map_md5 = maps.md5 '
        'ORDER BY scores.id DESC LIMIT 5'
    )

    return await render_template(
        'admin/home.html', dashdata=dash_data,
        recentusers=recent_users, recentscores=recent_scores,
        datetime=datetime, timeago=timeago
    )

@admin.route("/users", methods=["GET"])
@priv_check(priv=Privileges.Staff)
async def users():
    query_data = await db_utils.get_users()
    return await render_template("/admin/users/index.html", query_data=query_data)

@admin.route("/users/search/<user>", methods=["GET"])
@priv_check(priv=Privileges.Staff)
async def users_search(user: str):
    query_data = await db_utils.get_users(search=user)
    return await render_template(
        "/admin/users/index.html", query_data=query_data, search_value=user
    )

@admin.route("/user/<id>/edit")
@priv_check(priv=Privileges.Staff)
async def users_edit(id: int):
    query = await db_utils.get_user(id)
    return await render_template("admin/users/edit.html", search_data=query)

@admin.route("/user/<id>/update", methods=["POST"])
@priv_check(priv=Privileges.Staff)
async def users_update(id: int):
    try:
        form = await request.form

        db_data: dict = await db_utils.get_user(id)

        new_data = dict(
            name=form.get('edit-username', type=str),
            safe_name=utils.get_safe_name(form.get('edit-username', type=str)),
            email=form.get('edit-email', type=str),
            country=form.get('edit-country', type=str),
        )

        if form.get('actions', type=str) == "restricted":
            new_data["priv"] = 2
        elif db_data["priv"] == 2 and form.get('actions', type=str) == "unrestricted":
            new_data["priv"] = 3
        
        if form.get('password', type=str) != "":
            pw_md5 = hashlib.md5(form.get('password', type=str).encode()).hexdigest().encode()
            pw_bcrypt = bcrypt.hashpw(pw_md5, bcrypt.gensalt())

            await glob.db.execute(
                "UPDATE users "
                "SET pw_bcrypt = %s "
                "WHERE id = %s",
                [pw_bcrypt, id]
            )
        
        await db_utils.update("users", ("id", id), **dict_cmp(new_data, db_data))
        return redirect(f"/admin/users/search/{id}")
    except:
        return redirect("/admin/users")