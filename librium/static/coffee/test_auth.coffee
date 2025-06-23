# Test script for authentication functionality
# This file contains functions for testing the authentication system

# Test authentication
testAuthentication = ->
  console.log("Testing authentication...")
  
  # Test credentials
  username = "admin"
  password = "admin"
  
  # Request authentication token
  requestAuthToken(username, password)
    .then (token) ->
      console.log("Authentication successful. Token:", token)
      
      # Test token storage
      storedToken = getAuthToken()
      console.log("Stored token:", storedToken)
      
      # Test API call with token
      testApiCall()
    .catch (error) ->
      console.error("Authentication failed:", error)

# Test API call with token
testApiCall = ->
  console.log("Testing API call with token...")
  
  # Make a test API call to the protected endpoint
  $.ajax
    url: "/api/v1/protected"
    type: "GET"
    success: (response) ->
      console.log("API call successful:", response)
    error: (error) ->
      console.error("API call failed:", error)

# Export test functions
window.testAuthentication = testAuthentication
window.testApiCall = testApiCall

# Run tests when the document is ready
$ ->
  # Uncomment to run tests automatically
  # testAuthentication()