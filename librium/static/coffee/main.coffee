$ ->
  $("#cancel").click ->
    window.location.href = $(@).data "url"

  $applicableToggle = $ "input[name=applicable]"
  $changeInput = $ "input#change"
  $assigneeSelect = $ "select#assignee"
  $resolvedInput = $ "input#resolved"
  $appY = $ "#applicableY"
  $appN = $ "#applicableN"
  $confirmers = $("#resolve, #validate")

  $confirmers.click ->
    $.post $(@).data "url"
    window.location.reload()

  $(".notification > .delete").click ->
    $(@).parent().remove()

  $applicableToggle.change ->
    if $(@).val() is "1"
      $changeInput.prop "readonly", false
      $changeInput.removeClass "is-static"
      $assigneeSelect.prop "disabled", false
      $assigneeSelect.val $("[name=user]").val()
    else
      $changeInput.prop "readonly", true
      $changeInput.addClass "is-static"
      $assigneeSelect.prop "disabled", true
      $assigneeSelect.val $assigneeSelect.defaultSelected

  if not $applicableToggle.attr("checked") and not $applicableToggle.prop "disabled"
    $applicableToggle.prop "indeterminate", true

  $resolvedInput.change ->
    $(@).toggleClass "is-success"

  $("input[name=applicable]").change ->
    if $appY.prop "checked"
      $appY.addClass "is-success"
      $appN.removeClass "is-danger"
    if $appN.prop "checked"
      $appY.removeClass "is-success"
      $appN.addClass "is-danger"

  $("#reset").click ->
    if not ($appY.prop("disabled") or $appN.prop("disabled"))
      $appY.removeClass "is-success"
      $appN.removeClass "is-danger"
      $changeInput.prop "readonly", true
      $changeInput.addClass "is-static"
      $assigneeSelect.prop "disabled", true

  $("#attachment-button").click ->
    $(@).blur()
    $("html").addClass "is-clipped"
    $(".modal").toggleClass "is-active"

  $(".modal-background, .modal .delete, .modal button.is-danger").click ->
    $("html").removeClass "is-clipped"
    $(".modal").toggleClass "is-active"

  $(".file-input").change ->
    file = $(@)[0].files[0]
    $(".file-name").text(file.name)

  $("#upload button[type=submit]").click ->
    $("#upload form").submit()

  $(".attachment.delete").click ->
    url = $(@).data "url"
    hash = $(@).data "hash"
    pid = $(@).data "pid"
    parent = $(@).parent()
    data = JSON.stringify
      hash: hash
      pid: pid

    $.ajaxSetup
      contentType: "application/json"
    $.post url,
      data
    .done (data, status) ->
      parent.remove()