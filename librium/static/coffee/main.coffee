$ ->
#  M.AutoInit()
  $ ".ui.accordion"
    .accordion()
  $ "select.dropdown, .ui.dropdown"
    .dropdown
      allowAdditions: true
  $ ".ui.checkbox"
    .checkbox()
  $ "label > a, h4 > a"
    .popup()