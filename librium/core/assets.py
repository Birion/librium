from typing import Dict
from flask_assets import Bundle, Environment

# Asset paths
JS_VENDOR_PATH = "js/vendor/**/**/*.js"
SASS_VENDOR_PATH = "sass/vendor/**/*.sass"
SCSS_VENDOR_PATH = "scss/vendor/**/**/*.scss"
CSS_VENDOR_PATH = "css/vendor/**/**/*.css"
SASS_PERSONAL_PATH = "sass/*.sass"
COFFEE_PERSONAL_PATH = "coffee/*.coffee"

# Output paths
JS_OUTPUT_PATH = "gen/packed.js"
CSS_OUTPUT_PATH = "gen/packed.css"

# Filter configurations
SASS_FILTER = ["libsass"]
SCSS_FILTER = ["pyscss"]
JS_FILTER = ["jsmin"]
CSS_FILTER = ["cssutils"]
COFFEE_FILTER = ["coffeescript"]


def create_vendor_bundles() -> tuple[Bundle, Bundle, Bundle, Bundle]:
    """Create bundles for vendor assets."""
    js_bundle = Bundle(JS_VENDOR_PATH)
    sass_bundle = Bundle(SASS_VENDOR_PATH, filters=SASS_FILTER)
    scss_bundle = Bundle(SCSS_VENDOR_PATH, filters=SCSS_FILTER)
    css_bundle = Bundle(CSS_VENDOR_PATH)
    return js_bundle, sass_bundle, scss_bundle, css_bundle


def create_personal_bundles() -> tuple[Bundle, Bundle]:
    """Create bundles for personal assets."""
    sass_bundle = Bundle(SASS_PERSONAL_PATH, filters=SASS_FILTER, depends="sass/**/*.sass")
    js_bundle = Bundle(COFFEE_PERSONAL_PATH, filters=COFFEE_FILTER)
    return sass_bundle, js_bundle


def create_asset_bundles() -> Dict[str, Bundle]:
    """Create and configure all asset bundles."""
    vendor_js, vendor_sass, vendor_scss, vendor_css = create_vendor_bundles()
    personal_sass, personal_js = create_personal_bundles()

    return {
        "all-js": Bundle(
            vendor_js,
            personal_js,
            filters=JS_FILTER,
            output=JS_OUTPUT_PATH
        ),
        "all-css": Bundle(
            vendor_sass,
            vendor_scss,
            vendor_css,
            personal_sass,
            filters=CSS_FILTER,
            output=CSS_OUTPUT_PATH,
            depends="sass/**/*.sass"
        )
    }


assets = Environment()
bundles = create_asset_bundles()
assets.register(bundles)
