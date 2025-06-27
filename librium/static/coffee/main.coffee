# Main application initialization
# This file contains core UI initialization and common functionality

# Initialize UI components when the document is ready
$ ->
  initializeSemanticElements()
  initializeCoverToggle()
  initializeFilterChanges()
  initializeExportDownload()
  initializeSearch()

# Initialize Semantic UI components
initializeSemanticElements = ->
  $ ".ui.accordion"
    .accordion()

  $ "select.dropdown, .ui.dropdown"
    .dropdown
      fullTextSearch: true
      on: "hover"

  $ ".ui.checkbox"
    .checkbox()

  $ "*[data-content]"
    .popup()

# Cover Toggle functionality
initializeCoverToggle = ->
  $ "#cover-toggle"
    .click ->
      isCoverHidden = @.dataset["toggled"] == "false"

      # Update toggle state
      @.dataset["toggled"] = if isCoverHidden then "true" else "false"
      @.dataset["content"] = if isCoverHidden then "Show cover art" else "Hide cover art"
      @.classList.replace(
        if isCoverHidden then "green" else "red",
        if isCoverHidden then "red" else "green"
      )

      # Toggle cover visibility
      $ "img.ui.bordered.fluid.image"
        .toggleClass "hidden", isCoverHidden

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
