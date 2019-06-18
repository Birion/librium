$ ->

  $lastID = 0
  $seriesInputs = $ "input[name^=series-name]"

  $ ".ui.modal"
    .modal "attach events", ".new-link", "show"

  if $seriesInputs.length
    s = $seriesInputs.last()
    $lastID = Number(s.attr("name")[s.attr("name").length - 1])

  updateDropdown = (id, value, text) ->
    dropdown = $ "##{id}s"
    option = $ "<option/>",
      value: value
      text: text
    dropdown.append option
    dropdown.dropdown "refresh"

  $ "form#book"
    .submit (event) ->
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

      $.getJSON "/api/series",
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
              updateDropdown $type, data.id, data.name
