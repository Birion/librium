from sqlalchemy import desc, asc


def get_all(table, **kwargs):
    offset = kwargs["offset"]
    length = kwargs["offset"] + kwargs["length"]
    column = kwargs["sort"]
    f = asc if kwargs["asc"] else desc
    return [
        {"id": pub.id, "name": pub.name}
        for pub in table.query.order_by(f(column))[offset:length]
    ]
