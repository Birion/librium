from flask_assets import Bundle, Environment

assets = Environment()

vendor_js = Bundle("js/vendor/**/**/*.js")
vendor_sass = Bundle("sass/vendor/**/*.sass", filters=["libsass"])
vendor_scss = Bundle("scss/vendor/**/**/*.scss", filters=["pyscss"])
vendor_css = Bundle("css/vendor/**/**/*.css")
personal_sass = Bundle("sass/*.sass", filters=["libsass"], depends="sass/**/*.sass")
personal_js = Bundle("coffee/*.coffee", filters=["coffeescript"])

bundles = {
    "all-js": Bundle(vendor_js, personal_js, filters=["jsmin"], output="gen/packed.js"),
    "all-css": Bundle(
        vendor_sass,
        vendor_scss,
        vendor_css,
        personal_sass,
        filters=["cssutils"],
        output="gen/packed.css",
        depends="sass/**/*.sass",
    ),
}

assets.register(bundles)
