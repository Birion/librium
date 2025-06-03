from typing import Dict

from flask_assets import Bundle, Environment

# Asset paths
SASS_PERSONAL_PATH = "sass/*.sass"
COFFEE_PERSONAL_PATH = "coffee/*.coffee"

# Output paths
JS_OUTPUT_PATH = "gen/packed.js"
CSS_OUTPUT_PATH = "gen/packed.css"

# Filter configurations
SASS_FILTER = "libsass"
SCSS_FILTER = "pyscss"
JS_FILTER = "jsmin"
CSS_FILTER = "cssutils"
COFFEE_FILTER = "coffeescript"

# Dependencies
DEPENDS_SASS = "sass/**/*.sass"


def create_asset_bundles() -> Dict[str, Bundle]:
    """Create and configure all asset bundles."""
    return {
        "all-js": Bundle(
            COFFEE_PERSONAL_PATH,
            filters=[COFFEE_FILTER, JS_FILTER],
            output=JS_OUTPUT_PATH,
        ),
        "all-css": Bundle(
            SASS_PERSONAL_PATH,
            filters=[SASS_FILTER, CSS_FILTER],
            output=CSS_OUTPUT_PATH,
            depends=DEPENDS_SASS,
        ),
    }


assets = Environment()
bundles = create_asset_bundles()
assets.register(bundles)
