ns = {}

ns.model = do ->
  $eventPump = $ "body"

  init: (rtype, _id=null) ->
    ajaxOptions =
      type: "GET"
      url: if _id then "/api/#{rtype}/#{_id}" else "/api/#{rtype}"
      accepts: "application/json"
      dataType: "json"
    $.ajax ajaxOptions
      .done (data) ->
        $eventPump.trigger "model_init_success", [data, rtype]
      .fail (xhr, textStatus, errorThrown) ->
        $eventPump.trigger "model_error", [xhr, textStatus, errorThrown]

  read: (rtype, _id=null) ->
    ajaxOptions =
      type: "GET"
      url: if _id then "/api/#{rtype}/#{_id}" else "/api/#{rtype}"
      accepts: "application/json"
      dataType: "json"
    $.ajax ajaxOptions
      .done (data) ->
        $eventPump.trigger "model_read_success", [data]
      .fail (xhr, textStatus, errorThrown) ->
        $eventPump.trigger "model_error", [xhr, textStatus, errorThrown]

ns.view = do ->
  $dropdown = $ ".ui.dropdown"

  updateDropdown: (vals) ->
    console.log vals

ns.controller = do (m=ns.model, v=ns.view) ->
  model = m
  view = v
  $eventPump = $ "body"
  bookID = $("#_id").val()
  values = {}

  setTimeout ->
    model.init "book", bookID
    model.init "authors"
    model.init "formats"
    console.log values["formats"]
    view.updateDropdown values.formats
  , 100

  $eventPump.on "model_init_success", (e, data, rtype) ->
    values[rtype] = data

  $eventPump.on "model_read_success", (e, data) ->
    console.log data

  $eventPump.on "model_error", (e, xhr, textStatus, errorThrown) ->
    error_msg = "#{textStatus}: #{errorThrown} - #{xhr.responseJSON.detail}"
#    view.error error_msg
    console.log error_msg
