# Login functionality
# This file contains functions for handling user login and authentication

# Initialize login functionality when the document is ready
$ ->
  # Initialize login modal
  initializeLoginModal()
  
  # Check if we need to show the login modal on page load
  checkAuthenticationStatus()

# Initialize the login modal
initializeLoginModal = ->
  # Initialize the login modal
  $loginModal = $("#login-modal")
  
  # Handle login form submission
  $("#login-form").submit (event) ->
    event.preventDefault()
    username = $("#username").val()
    password = $("#password").val()
    
    # Disable form during authentication
    $("#login-submit").addClass("loading disabled")
    
    # Request authentication token
    requestAuthToken(username, password)
      .done ->
        # Close modal on success
        $loginModal.modal("hide")
      .fail (error) ->
        # Show error message
        $("#login-error").text(error.responseJSON?.msg || "Authentication failed")
        $("#login-error").show()
      .always ->
        # Re-enable form
        $("#login-submit").removeClass("loading disabled")

# Check if user is authenticated and show login modal if not
checkAuthenticationStatus = ->
  # If no token is stored, show the login modal
  if !hasAuthToken()
    showLoginModal()
  else
    # Verify the token is valid by making a test request
    $.ajax
      url: document.querySelector("meta[name='test-url']").getAttribute("content")
      type: "GET"
      error: (xhr) ->
        if xhr.status == 401
          # Token is invalid, clear it and show login modal
          clearAuthToken()
          showLoginModal()

# Show the login modal
showLoginModal = ->
  $("#login-modal").modal
    closable: false
    onVisible: ->
      # Clear any previous error messages
      $("#login-error").hide()
      # Focus on username field
      $("#username").focus()
  .modal("show")

# Export functions for use in other modules
window.showLoginModal = showLoginModal
window.checkAuthenticationStatus = checkAuthenticationStatus