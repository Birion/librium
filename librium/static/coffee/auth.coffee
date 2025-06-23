# Authentication functionality
# This file contains functions for handling authentication tokens

# Constants
TOKEN_STORAGE_KEY = "librium_auth_token"

# Request an authentication token from the server
# @param {string} username - The username for authentication
# @param {string} password - The password for authentication
# @return {Promise} A promise that resolves with the token or rejects with an error
requestAuthToken = (username, password) ->
  # Create form data for authentication request
  formData = new FormData()
  formData.append("username", username)
  formData.append("password", password)
  
  # Send authentication request
  $.ajax
    url: "/api/v1/auth/token"
    type: "POST"
    data: formData
    processData: false
    contentType: false
  .done (response) ->
    # Store the token and return it
    storeAuthToken(response.access_token)
    return response.access_token
  .fail (error) ->
    console.error("Authentication failed:", error)
    throw error

# Store the authentication token
# @param {string} token - The authentication token to store
storeAuthToken = (token) ->
  localStorage.setItem(TOKEN_STORAGE_KEY, token)

# Get the stored authentication token
# @return {string|null} The stored token or null if not found
getAuthToken = ->
  localStorage.getItem(TOKEN_STORAGE_KEY)

# Check if an authentication token is stored
# @return {boolean} True if a token is stored, false otherwise
hasAuthToken = ->
  !!getAuthToken()

# Clear the stored authentication token
clearAuthToken = ->
  localStorage.removeItem(TOKEN_STORAGE_KEY)

# Add the authentication token to AJAX requests
setupAjaxAuth = ->
  $.ajaxSetup
    beforeSend: (xhr) ->
      token = getAuthToken()
      if token
        xhr.setRequestHeader("Authorization", "Bearer #{token}")

# Initialize authentication when the document is ready
$ ->
  # Set up AJAX authentication
  setupAjaxAuth()

# Export functions for use in other modules
window.requestAuthToken = requestAuthToken
window.getAuthToken = getAuthToken
window.hasAuthToken = hasAuthToken
window.clearAuthToken = clearAuthToken