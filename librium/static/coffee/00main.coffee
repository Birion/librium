$ ->
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
      url = new URL $(@).data "url"
      url.searchParams.append key, val
      window.location = url.toString()

#  Cover Toggle

  $ "#cover-toggle"
    .click ->
      if @.dataset["toggled"] == "false"
        @.dataset["toggled"] = "true"
        @.dataset["content"] = "Show cover art"
        @.classList.replace "green", "red"
        $ "img.ui.bordered.fluid.image"
          .addClass "hidden"
      else
        @.dataset["toggled"] = "false"
        @.dataset["content"] = "Hide cover art"
        @.classList.replace "red", "green"
        $ "img.ui.bordered.fluid.image"
          .removeClass "hidden"

showWarning = (message) ->
  console.log message
  $.toast
    class: "error"
    position: "top attached"
    message: message
