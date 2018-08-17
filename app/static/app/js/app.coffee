$ ->
    set_active_navbar()
    $("[data-toggle='tooltip']").tooltip()
    $("[data-toggle='popover']").popover()
    $("#video-like-btn").click(video_affinity)
    $("#video-dislike-btn").click(video_affinity)
    init_video_like_btn()
    $("#search-form").on("submit", search)
    init_datepicker()

set_active_navbar = ->
    $(".section-nav").each (i, obj) ->
        li = $(@)
        li.removeClass("active")

    $("##{active_section_nav}").addClass("active")

init_video_like_btn = ->
    if already_liked? and already_liked == "False"
        $("#video-dislike-btn").hide()
    else
        $("#video-like-btn").hide()

video_affinity = (event) ->
    event.preventDefault()
    url = this.pathname
    button_id = this.id
    $.get url, (data) ->
        data = JSON.parse(data)
        $("#video_likes_count").text(data.count)
        if button_id == "video-like-btn"
            $("#video-like-btn").hide()
            $("#video-dislike-btn").fadeIn(500)
        else
            $("#video-dislike-btn").hide()
            $("#video-like-btn").fadeIn(500)            
        $("#likes-heart ").attr("data-original-title", data.likes.join("<br/>"))

search = (event) ->
    event.preventDefault()
    data = $("#search-input").val()
    url1 = $(this).attr("action")
    url = "#{url1}#{data}/"
    window.location.href = url

init_datepicker = ->
    $(".datepicker").datepicker
        changeMonth: true,
        changeYear: true,
        yearRange: "1940:"
        dateFormat: "dd/mm/yy"
