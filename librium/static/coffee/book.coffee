$ ->

  $lastID = 0
  $seriesInputs = $ "input[name^=series-name]"

  $ "#new-modal"
    .modal "attach events", ".new-link", "show"
  $ "#cover-modal"
    .modal "attach events", "img[alt$='cover']", "show"

  if $seriesInputs.length
    s = $seriesInputs.last()
    $lastID = Number(s.attr("name")[s.attr("name").length - 1])

  updateDropdown = (id, value, text) ->
    dropdown = $ "input[name=#{id}s]"
      .parent()
    menu = dropdown.find(".menu")
    option = $ "<div/>",
      class: "item"
      text: text
    option.attr("data-value", value)
    menu.append option
    dropdown.dropdown "refresh"

  getVal = (f) ->
    if f.name == "read"
      f.checked
    else
      f.value

  class Values
    constructor: (@inputs) ->
      @[f.name] = getVal f for f in @inputs when f.name != "" and f.value != ""
      delete @inputs

  $ "form#book"
    .submit (_event) ->
      $series = $ "#series"
      seriesArray = []
      for s in $ "input[name^=series-name]"
        name = s.value
        idx = $("#series-index-#{s.name[s.name.length - 1]}").val()
        si =
          series: name
          idx: idx
        seriesArray.push si
      $series.val JSON.stringify(seriesArray)

  $ ".remove.series"
    .click ->
      $(@).parents(".fields").remove()

  $ "#add-series"
    .click ->
      $lastID++

      makeDiv = (_class) ->
        $ "<div/>",
          "class": _class

      makeLabel = (target) ->
        $ "<label/>",
          for: "series-#{target}-#{$lastID}"
          text: target[0].toUpperCase() + target[1...]

      makeLink = (type, icon) ->
        $ "<a/>",
          "class": "ui teal button #{type}" + " series"
        .append $ "<i/>",
          "class": "#{icon}" +" icon"

      $field = makeDiv "fields"
      $(@).parent().before $field

      $idxField = makeDiv "one wide field"
      $idxField.appendTo $field

      $emptyField = $idxField.clone()
      $emptyField.prependTo $field

      $idxLabel = makeLabel "index"
      $idxLabel.appendTo $idxField

      $ "<input/>",
        name: "series-index-#{$lastID}"
        id: "series-index-#{$lastID}"
        type: "number"
        min: 0
        step: 0.1
      .appendTo $idxField

      $seriesField = makeDiv "eight wide field"
      $seriesField.prependTo $field

      $seriesLabel = makeLabel "name"
      $seriesLabel.appendTo $seriesField

      $buttonsDiv = makeDiv "ui fluid buttons"
      $buttonsDiv.appendTo $seriesField

      $buttonDiv = makeDiv "ui fluid dropdown search icon button"
      $buttonDiv.appendTo $buttonsDiv

      $ "<input/>",
        type: "hidden"
        name: "series-name-#{$lastID}"
      .appendTo $buttonDiv

      $ "<span/>",
        class: "text"
        text: "Select series"
      .appendTo $buttonDiv

      $menuDiv = makeDiv "menu"
      $menuDiv.appendTo $buttonDiv

      $editLink = makeLink "edit", "pencil"
      $editLink.appendTo $buttonsDiv
      $removeLink = makeLink "remove", "minus"
      $removeLink.appendTo $buttonsDiv

      $.getJSON $(@).data("url"),
        [],
        (data) ->
          for item in data
            console.log item
            _ = $ "<div/>",
              class: "item"
              "data-value": item.id
              text: item.name
            _.appendTo $menuDiv
          $buttonDiv.dropdown()

  $ ".new-link"
    .click ->
      $type = $( @ ).data "type"
      $modal = $ ".ui.modal"
      $modal.children ".header"
        .text "Create a new #{$type}"
      $modal.modal
        onApprove: ->
          $.post $modal.data("url"),
            name: $modal.find("#name").val()
            type: $type
            ,
            (data) ->
              $modal.find("#name").val(null)
              updateDropdown $type, data.id, data.name

  $ "#book"
    .submit (event) ->
      event.preventDefault()
      values = new Values $( @ ).find("input, select#format")
      $.post @.action,
        values
        ,
        (data) ->
          window.location = data.url

  $ "#fileinput"
    .change ->
     url = @.dataset["url"]
     if @.files? and @.files.length > 0
       file = @.files[0]
       formData = new FormData
       formData.append "cover", file
       formData.append "uuid", $("#uuid").val()
       $.ajax
         url: url
         type: "POST"
         data: formData
         processData: false
         contentType: false
       .done ->
         window.location.reload()