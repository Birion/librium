# Main application initialization
# This file contains core UI initialization and common functionality

# Initialize UI components when the document is ready
$ ->
  initializeSemanticElements()
  initializeFilterChanges()
  initializeExportDownload()
  initializeSearch()
  initializeSidebar()
  initializeKeyboardNavigation()

# Initialize Semantic UI components
initializeSemanticElements = ->
  $ ".ui.accordion"
    .accordion
      onOpening: ->
        $(@).prev(".title").attr("aria-expanded", "true")
        $(@).attr("aria-hidden", "false")
      onClosing: ->
        $(@).prev(".title").attr("aria-expanded", "false")
        $(@).attr("aria-hidden", "true")

  $ "select.dropdown, .ui.dropdown"
    .dropdown
      fullTextSearch: true
      on: "hover"
      onShow: ->
        $(@).attr("aria-expanded", "true")
      onHide: ->
        $(@).attr("aria-expanded", "false")

  $ ".ui.checkbox"
    .checkbox()

  $ "*[data-content]"
    .popup()

initializeKeyboardNavigation = ->
  # Handle Enter/Space on role="button" and tabindex="0" elements
  $ "[role='button'][tabindex='0'], [role='menuitem'][tabindex='0']"
    .on "keydown", (e) ->
      if e.which == 13 or e.which == 32 # Enter or Space
        e.preventDefault()
        $(@).click()

  # Specific handler for accordion titles to allow keyboard toggling if not handled by Fomantic
  $ ".ui.accordion .title[tabindex='0']"
    .on "keydown", (e) ->
      if e.which == 13 or e.which == 32
        e.preventDefault()
        $(@).parent().accordion('toggle', $(@).index() / 2)

initializeSidebar = ->
  # Initialize sidebar
  $ "#main-sidebar"
    .sidebar
      transition: "overlay"
      mobileTransition: "uncover"

  # Sidebar toggle button
  $ "#sidebar-toggle"
    .click ->
      $ "#main-sidebar"
        .sidebar "toggle"

# Handle filter changes
initializeFilterChanges = ->
  $ "#filter"
    .change ->
      key = $(@).data "type"
      val = @.value
      url = new URL $(@).data "url"
      url.searchParams.append key, val
      window.location = url.toString()

initializeExportDownload = ->
  $ ".export.link.item"
    .click ->
      $filename = $(@).data "filename"
      $url = $(@).data "url"
      $.ajax
        url: $url
        type: "GET"
        success: (data) ->
          # If the response is a JSON object, stringify it
          if typeof data is "object"
            data = JSON.stringify(data, null, 2)
          # Create a blob from the data and trigger download
          blob = new Blob([data], { type: "application/octet-stream" })
          link = document.createElement("a")
          link.href = URL.createObjectURL(blob)
          link.download = $filename || "export.zip"
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        error: (error) ->
          showWarning error.responseText

initializeSearch = ->
  $ ".sidebar .item form i"
    .click ->
      $(@).closest("form").submit()

# Display a warning toast message
# @param {string} message - The message to display
showWarning = (message) ->
  console.log message
  $.toast
    class: "error"
    position: "top attached"
    message: message

# Export functions for use in other modules
window.showWarning = showWarning
