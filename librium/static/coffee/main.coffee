# Main application initialization
# This file contains core UI initialization and common functionality

# Initialize UI components when the document is ready
$ ->
  # Initialize Semantic UI components
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

  # Handle filter changes
  $ "#filter"
    .change ->
      key = $(@).data "type"
      val = @.value
      url = new URL $(@).data "url"
      url.searchParams.append key, val
      window.location = url.toString()

  # Cover Toggle functionality
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
