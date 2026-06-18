from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from librium.core.logging import get_logger
from librium.services import (
    AuthorService,
    FormatService,
    GenreService,
    LanguageService,
    PublisherService,
    SeriesService,
)

logger = get_logger("views.manage")

bp = Blueprint("manage", __name__, url_prefix="/manage")

# Registry that maps a URL slug to its service and display label
ENTITY_REGISTRY = {
    "authors": {
        "service": AuthorService,
        "label": "Authors",
        "singular": "Author",
        "fields": ["name"],
    },
    "genres": {
        "service": GenreService,
        "label": "Genres",
        "singular": "Genre",
        "fields": ["name"],
    },
    "series": {
        "service": SeriesService,
        "label": "Series",
        "singular": "Series",
        "fields": ["name"],
    },
    "publishers": {
        "service": PublisherService,
        "label": "Publishers",
        "singular": "Publisher",
        "fields": ["name"],
    },
    "formats": {
        "service": FormatService,
        "label": "Formats",
        "singular": "Format",
        "fields": ["name"],
    },
    "languages": {
        "service": LanguageService,
        "label": "Languages",
        "singular": "Language",
        "fields": ["name"],
    },
}


def _get_registry_or_404(entity_type: str):
    """Return the registry entry for *entity_type* or abort with 404."""
    entry = ENTITY_REGISTRY.get(entity_type)
    if entry is None:
        from flask import abort

        abort(404)
    return entry


@bp.route("/")
def index():
    """Management landing page – links to each entity list."""
    return render_template(
        "manage/index.html",
        entities=ENTITY_REGISTRY,
    )


@bp.route("/<entity_type>")
def entity_list(entity_type):
    """List all items of a given entity type."""
    entry = _get_registry_or_404(entity_type)
    service = entry["service"]
    items = service.get_all()
    return render_template(
        "manage/list.html",
        items=items,
        entity_type=entity_type,
        entry=entry,
        entities=ENTITY_REGISTRY,
    )


@bp.route("/<entity_type>/new", methods=["GET", "POST"])
def entity_new(entity_type):
    """Create a new entity item."""
    entry = _get_registry_or_404(entity_type)
    service = entry["service"]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return render_template(
                "manage/form.html",
                item=None,
                entity_type=entity_type,
                entry=entry,
                entities=ENTITY_REGISTRY,
                error="Name cannot be empty.",
            )
        try:
            if entity_type == "authors":
                service.create_by_name(name)
            else:
                service.create(name=name)
            return redirect(url_for("manage.entity_list", entity_type=entity_type))
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error creating {entry['singular']}: {e}")
            return render_template(
                "manage/form.html",
                item=None,
                entity_type=entity_type,
                entry=entry,
                entities=ENTITY_REGISTRY,
                error=str(e),
            )

    return render_template(
        "manage/form.html",
        item=None,
        entity_type=entity_type,
        entry=entry,
        entities=ENTITY_REGISTRY,
        error=None,
    )


@bp.route("/<entity_type>/edit/<int:item_id>", methods=["GET", "POST"])
def entity_edit(entity_type, item_id):
    """Edit an existing entity item."""
    entry = _get_registry_or_404(entity_type)
    service = entry["service"]

    item = service.get_by_id(item_id)
    if not item:
        return redirect(url_for("manage.entity_list", entity_type=entity_type))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return render_template(
                "manage/form.html",
                item=item,
                entity_type=entity_type,
                entry=entry,
                entities=ENTITY_REGISTRY,
                error="Name cannot be empty.",
            )
        try:
            if entity_type == "authors":
                service.update(item_id, name=name)
            else:
                service.update(item_id, name=name)
            return redirect(url_for("manage.entity_list", entity_type=entity_type))
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error updating {entry['singular']} {item_id}: {e}")
            return render_template(
                "manage/form.html",
                item=item,
                entity_type=entity_type,
                entry=entry,
                entities=ENTITY_REGISTRY,
                error=str(e),
            )

    return render_template(
        "manage/form.html",
        item=item,
        entity_type=entity_type,
        entry=entry,
        entities=ENTITY_REGISTRY,
        error=None,
    )


@bp.route("/<entity_type>/delete/<int:item_id>", methods=["POST"])
def entity_delete(entity_type, item_id):
    """Soft-delete an entity item."""
    entry = _get_registry_or_404(entity_type)
    service = entry["service"]

    try:
        service.delete(item_id)
    except (ValueError, SQLAlchemyError) as e:
        logger.error(f"Error deleting {entry['singular']} {item_id}: {e}")

    return redirect(url_for("manage.entity_list", entity_type=entity_type))
