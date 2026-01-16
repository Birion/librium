# Book management functionality
# This file contains all the JavaScript functionality related to book management,
# including form handling, series management, and cover uploads.

# Track the last series ID for dynamic series field creation
$lastID = 0
$seriesInputs = $ "input[name^=series-name]"

# Initialize book-related functionality when the document is ready
$ ->

  # Initialize the last ID from existing series inputs
  if $seriesInputs.length
    s = $seriesInputs.last()
    $lastID = Number(s.attr("name")[s.attr("name").length - 1])

  # Initialize modals
  initializeModals()

  # Initialize form handlers
  initializeFormHandlers()

  # Initialize series management
  initializeSeriesManagement()

  # Initialize file upload
  initializeFileUpload()

# ===== Modal Initialization =====

# Initialize all modals used in book management
initializeModals = ->
  # New entity modal
  $ "#new-modal"
    .modal "attach events", ".new-link", "show"

  # Cover image modal
  $ "#cover-modal"
    .modal "attach events", "img[alt$='cover']", "show"

  # Delete confirmation modal
  $ "#delete-modal"
    .modal "attach events", "#delete-book", "show"
    .modal onApprove: ->
      url = @.dataset["url"]
      id = parseInt @.dataset["id"]

      # Create form data for deletion request
      formData = new FormData
      formData.append "id", id

      # Send deletion request
      $.ajax
        url: url
        type: "POST"
        data: formData
        processData: false
        contentType: false
      .done (response) ->
        window.location = response.url

# ===== Utility Functions =====

# Update a dropdown with a new option
# @param {string} id - The ID of the dropdown to update
# @param {string|number} value - The value of the new option
# @param {string} text - The display text of the new option
updateDropdown = (id, value, text) ->
  dropdown = $ "input[name=#{id}s]"
    .parent()
  menu = dropdown.find(".menu")

  # Create new option element
  option = $ "<div/>",
    class: "item"
    text: text
  option.attr("data-value", value)

  # Add to menu and refresh dropdown
  menu.append option
  dropdown.dropdown "refresh"

# Get the value of a form field, handling special cases
# @param {HTMLElement} f - The form field element
# @return {*} The value of the field
getVal = (f) ->
  if f.name == "read"
    f.checked
  else
    f.value

# Class to collect form values
class Values
  # @param {Array<HTMLElement>} inputs - The form input elements
  constructor: (@inputs) ->
    # Add each non-empty field to the object
    @[f.name] = getVal f for f in @inputs when f.name != "" and f.value != ""
    delete @inputs

# ===== Form Handlers =====

# Initialize form submission handlers
initializeFormHandlers = ->
  # Handle series data collection on form submission
  $ "form#book"
    .submit (_event) ->
      $series = $ "#series"
      seriesArray = []

      # Collect series data from all series input fields
      for s in $ "input[name^=series-name]"
        name = s.value
        idx = $("#series-index-#{s.name[s.name.length - 1]}").val()
        si =
          series: name
          idx: idx
        seriesArray.push si

      # Store as JSON in hidden field
      $series.val JSON.stringify(seriesArray)

  # Handle book form submission with AJAX
  $ "#book"
    .submit (event) ->
      event.preventDefault()
      values = new Values $( @ ).find("input, select#format")

      # Submit form data via AJAX
      $.ajax
        type: "POST"
        url: @.action
        data: values
        success: (data) ->
          window.location = data.url
        error: (data) ->
          showWarning(data.responseJSON.error)

  # Handle new entity creation
  $ ".new-link"
    .click ->
      $type = $( @ ).data "type"
      $modal = $ "#new-modal"

      # Update modal title
      $modal.children ".header"
        .text "Create a new #{$type}"

      # Configure modal approval action
      $modal.modal
        onApprove: ->
          $.post $modal.data("url"),
            name: $modal.find("#name").val()
            type: $type
            (data) ->
              # Clear input and update dropdown
              $modal.find("#name").val(null)
              updateDropdown $type, data.id, data.name

# ===== Series Management =====

# Initialize series management functionality
initializeSeriesManagement = ->
  # Initialize existing dropdowns in the series section
  $ ".series .ui.dropdown"
    .dropdown
      on: "click"

  # Handle series removal
  $ ".remove.series"
    .click ->
      $(@).parents(".fields").remove()

  # Handle adding a new series
  $ "#add-series"
    .click ->
      $lastID++
      createSeriesFields($(@))

# Create a new set of series input fields
# @param {jQuery} $addButton - The add series button element
createSeriesFields = ($addButton) ->
  # Helper functions for creating elements
  makeDiv = (_class) ->
    $ "<div/>",
      "class": _class

  makeLabel = (target) ->
    $ "<label/>",
      for: "series-#{target}-#{$lastID}"
      text: target[0].toUpperCase() + target[1...]

  makeLink = (type, icon, color) ->
    $ "<a/>",
      "class": "ui #{color} icon button #{type} series"
    .append $ "<i/>",
      "class": "#{icon} icon"

  # Create the main field container
  $field = makeDiv "stackable fields"
  $addButton.parent().before $field

  # Create series field
  $seriesField = makeDiv "eight wide field"
  $seriesField.appendTo $field

  # Add series label
  $seriesLabel = makeLabel "name"
  $seriesLabel.appendTo $seriesField

  # Create selection dropdown
  $dropdownDiv = makeDiv "ui fluid search selection dropdown"
  $dropdownDiv.appendTo $seriesField

  # Add hidden input for series name
  $ "<input/>",
    type: "hidden"
    name: "series-name-#{$lastID}"
  .appendTo $dropdownDiv

  # Add dropdown icon
  $ "<i/>",
    class: "dropdown icon"
  .appendTo $dropdownDiv

  # Add dropdown text
  $ "<span/>",
    class: "text"
    text: "Select series"
  .appendTo $dropdownDiv

  # Create dropdown menu
  $menuDiv = makeDiv "menu"
  $menuDiv.appendTo $dropdownDiv

  # Create index field
  $idxField = makeDiv "six wide field"
  $idxField.appendTo $field

  # Add index label and input
  $idxLabel = makeLabel "index"
  $idxLabel.appendTo $idxField

  $ "<input/>",
    name: "series-index-#{$lastID}"
    id: "series-index-#{$lastID}"
    type: "number"
    min: 0
    step: 0.1
  .appendTo $idxField

  # Create button field
  $buttonField = makeDiv "two wide field"
  $buttonField.appendTo $field

  # Add button label
  $buttonLabel = $ "<label/>"
  $buttonLabel.appendTo $buttonField

  # Add remove button
  $removeLink = makeLink "remove", "minus", "red"
  $removeLink.appendTo $buttonField

  # Load series data from server
  $.getJSON $addButton.data("url"), [], (data) ->
    for item in data
      # Create menu item for each series
      menuItem = $ "<div/>",
        class: "item"
        "data-value": item.id
        text: item.name
      menuItem.appendTo $menuDiv

    # Initialize dropdown
    $dropdownDiv.dropdown
      on: "click"

  $field = $ ""

  initializeSeriesManagement()

# ===== File Upload =====

# Initialize file upload functionality
initializeFileUpload = ->
  $ "#fileinput"
    .change ->
      url = @.dataset["url"]
      if @.files? and @.files.length > 0
        file = @.files[0]

        # Create form data for file upload
        formData = new FormData
        formData.append "cover", file
        formData.append "uuid", $("#uuid").val()

        # Send upload request
        $.ajax
          url: url
          type: "POST"
          data: formData
          processData: false
          contentType: false
        .done ->
          window.location.reload()
