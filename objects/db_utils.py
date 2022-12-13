from quart import jsonify
from objects import glob


async def get_users(limit: int = 100, search: str = None):
    """Returns all user information."""
    query = """
        SELECT 
            u.*,
            l.ip,
            l.osu_ver,
            l.osu_stream,
            l.datetime AS last_login
        FROM users u
        LEFT join (
            SELECT * FROM ingame_logins i1
            INNER JOIN (
                SELECT max(id) AS max_id
                FROM ingame_logins
                GROUP BY userid
            ) AS i2
            ON i1.id = i2.max_id
        ) AS l
        ON u.id = l.userid
    """.replace(
        "  ", " "
    ).splitlines()
    
    args = []

    if search:
        query.append("WHERE u.`name` LIKE %s")
        args.append(f"{search}%")
        query.append("OR u.`email` LIKE %s")
        args.append(f"{search}%")
        query.append("OR CONVERT(u.`id`, char) LIKE %s")
        args.append(f"{search}%%")

    query.append(f"ORDER BY l.`datetime` DESC LIMIT %s")
    args.append(limit)

    query = " ".join(query)

    return await glob.db.fetchall(query, args)


async def get_user(id: int):
    """Returns a user information."""
    return await glob.db.fetch(
        f"SELECT * FROM users WHERE id={id}"
    )


async def update(table, id, **kargs):
    """Updates the fields of a table."""
    params = []

    for key, value in kargs.items():
        if value is not None:
            params.append(f"{key}='{value}'")
        else:
            params.append(f"{key}=NULL")
    
    await glob.db.execute(
        "UPDATE `%s` SET %s WHERE %s = '%s'" % (table, ", ".join(params), *id)
    )
    return 200