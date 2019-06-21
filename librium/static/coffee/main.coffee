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
