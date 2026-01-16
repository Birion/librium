from typing import Dict
from librium.__version__ import __version__

from flask_assets import Bundle, Environment

# Asset paths
SASS_PERSONAL_PATH = "sass/*.sass"
COFFEE_CORE_PATH = "coffee/main.coffee"
COFFEE_AUTH_PATH = "coffee/auth.coffee"
COFFEE_LOGIN_PATH = "coffee/login.coffee"
COFFEE_BOOK_PATH = "coffee/book.coffee"
COFFEE_VALIDATION_PATH = "coffee/validation.coffee"

# Output paths
JS_CORE_OUTPUT_PATH = f"gen/main.{__version__}.js"
JS_AUTH_OUTPUT_PATH = f"gen/auth.{__version__}.js"
JS_BOOK_OUTPUT_PATH = f"gen/book.{__version__}.js"
JS_VALIDATION_OUTPUT_PATH = f"gen/validation.{__version__}.js"
CSS_OUTPUT_PATH = f"gen/packed.{__version__}.css"

# Filter configurations
SASS_FILTER = "sass"
SCSS_FILTER = "pyscss"
JS_FILTER = "jsmin"
CSS_FILTER = "cssutils"
COFFEE_FILTER = "coffeescript"

# Dependencies
DEPENDS_SASS = "sass/**/*.sass"


def create_asset_bundles() -> Dict[str, Bundle]:
    """Create and configure all asset bundles."""
    return {
        # JavaScript bundles
        "js-core": Bundle(
            COFFEE_CORE_PATH,
            filters=[COFFEE_FILTER, JS_FILTER],
            output=f"{JS_CORE_OUTPUT_PATH}",
        ),
        "js-auth": Bundle(
            COFFEE_AUTH_PATH,
            COFFEE_LOGIN_PATH,
            filters=[COFFEE_FILTER, JS_FILTER],
            output=f"{JS_AUTH_OUTPUT_PATH}",
        ),
        "js-book": Bundle(
            COFFEE_BOOK_PATH,
            filters=[COFFEE_FILTER, JS_FILTER],
            output=f"{JS_BOOK_OUTPUT_PATH}",
        ),
        "js-validation": Bundle(
            COFFEE_VALIDATION_PATH,
            filters=[COFFEE_FILTER, JS_FILTER],
            output=f"{JS_VALIDATION_OUTPUT_PATH}",
        ),
        # CSS bundle
        "all-css": Bundle(
            SASS_PERSONAL_PATH,
            filters=[SASS_FILTER, CSS_FILTER],
            output=f"{CSS_OUTPUT_PATH}",
            depends=DEPENDS_SASS,
        ),
    }


assets = Environment()
bundles = create_asset_bundles()
assets.register(bundles)
