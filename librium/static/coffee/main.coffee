$ ->
#  M.AutoInit()
  $ ".ui.accordion"
    .accordion()
  $ "select.dropdown, .ui.dropdown"
    .dropdown
      fullTextSearch: true
  $ ".ui.checkbox"
    .checkbox()
  $ "*[data-content]"
    .popup()

  $ "#filter"
    .change ->
      key = $(@).data "type"
      val = @.value
      url = new URI $(@).data "url"
      data =
        "#{key}": val
      url.query data
      window.location = url.toString()

#  Cover Toggle

  $ "#cover-toggle"
    .click ->
      if @.dataset["toggled"] == "false"
        @.dataset["toggled"] = "true"
        @.innerText = "Show cover art"
        $ "img.ui.bordered.fluid.image"
        .addClass "hidden"
      else
        @.dataset["toggled"] = "false"
        @.innerText = "Hide cover art"
        $ "img.ui.bordered.fluid.image"
        .removeClass "hidden"
