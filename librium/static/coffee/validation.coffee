# Form validation functionality
# This file contains functions for validating form inputs

# Initialize validation when the document is ready
$ ->
  # Initialize form validation
  initializeFormValidation()

# Initialize form validation for all forms
initializeFormValidation = ->
  # Book form validation
  initializeBookFormValidation()
  
  # Login form validation
  initializeLoginFormValidation()

# Initialize validation for the book form
initializeBookFormValidation = ->
  $bookForm = $("#book")
  
  # Skip if the form doesn't exist on the current page
  return unless $bookForm.length
  
  # Add validation rules
  $bookForm.form
    fields:
      title:
        identifier: "title"
        rules: [
          {
            type: "empty"
            prompt: "Please enter a title"
          }
        ]
      format:
        identifier: "format"
        rules: [
          {
            type: "empty"
            prompt: "Please select a format"
          }
        ]
      authors:
        identifier: "authors"
        rules: [
          {
            type: "empty"
            prompt: "Please select at least one author"
          }
        ]
    
    # Custom validation for series
    onSuccess: (event, fields) ->
      # Check if series is valid
      $seriesInputs = $("input[name^=series-name]")
      if $seriesInputs.length > 0
        for input in $seriesInputs
          seriesValue = $(input).val()
          indexInput = $("#series-index-#{input.name[input.name.length - 1]}")
          indexValue = indexInput.val()
          
          # Series name must be selected if index is provided
          if indexValue && !seriesValue
            # Show error message
            $(".ui.error.message").html("<ul class='list'><li>Series must be selected if index is provided</li></ul>").show()
            event.preventDefault()
            return false
          
          # Index must be a non-negative number
          if seriesValue && indexValue && (isNaN(parseFloat(indexValue)) || parseFloat(indexValue) < 0)
            # Show error message
            $(".ui.error.message").html("<ul class='list'><li>Series index must be a non-negative number</li></ul>").show()
            event.preventDefault()
            return false
      
      # Validation passed
      return true

# Initialize validation for the login form
initializeLoginFormValidation = ->
  $loginForm = $("#login-form")
  
  # Skip if the form doesn't exist on the current page
  return unless $loginForm.length
  
  # Add validation rules
  $loginForm.form
    fields:
      username:
        identifier: "username"
        rules: [
          {
            type: "notEmpty"
            prompt: "Please enter a username"
          }
        ]
      password:
        identifier: "password"
        rules: [
          {
            type: " notEmpty"
            prompt: "Please enter a password"
          }
        ]

# Validate ISBN format
validateISBN = (isbn) ->
  return true unless isbn  # Empty is valid
  
  # Remove hyphens
  isbn = isbn.replace(/-/g, "")
  
  # Check length (10 or 13 digits)
  return false unless isbn.length in [10, 13]
  
  # Check if all characters are digits
  return false unless /^\d+$/.test(isbn)
  
  # Valid ISBN
  return true

# Validate year format
validateYear = (year) ->
  return true unless year  # Empty is valid
  
  # Convert to number
  year = parseInt(year)
  
  # Check if it's a valid year (between 1000 and 3000)
  return year >= 1000 && year < 3000

# Validate price format
validatePrice = (price) ->
  return true unless price  # Empty is valid
  
  # Convert to number
  price = parseFloat(price)
  
  # Check if it's a valid price (non-negative)
  return !isNaN(price) && price >= 0

# Validate page count format
validatePageCount = (pageCount) ->
  return true unless pageCount  # Empty is valid
  
  # Convert to number
  pageCount = parseInt(pageCount)
  
  # Check if it's a valid page count (positive)
  return !isNaN(pageCount) && pageCount > 0

# Export validation functions for use in other modules
window.validateISBN = validateISBN
window.validateYear = validateYear
window.validatePrice = validatePrice
window.validatePageCount = validatePageCount