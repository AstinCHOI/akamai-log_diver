$("#combobox").combobox();
        
$(".hidden_links").hide();
$(".hidden_controls").hide();

$("#input_url").bind('keydown', function(e) {
  if (e.keyCode == 13) {
    $("#submit").click();
  }
});

$("#submit").click(function() { 
  // socket.on('connect', function() {
  //   console.log("socket.io connected");
  // });

  var progress = 1;
  var progressVar = setInterval(progressTimer, 1000);
  var progressLogdiver = 0;
  function progressTimer() {
    if(progress < 30) {
      progress += Math.floor((Math.random() * 12) + 1);
    } else if(progress <= progressLogdiver) {
      progress = progressLogdiver;
    } 

    $('#progress_bar').attr('style', 'width: ' + progress + '%');
    if(progress >= 100) {
      window.clearInterval(progressVar);
    }
  }

  function init() {
    progress = 1;
    progressLogdiver = 0;
    
    $('#req_header').text('');
    $('#progress_bar').removeClass('progress-bar-warning');
    $('#progress_bar').attr('style', 'width: 1%');
    $('#console').text('');
    $('#result_response_header').text('');
    $('.result_logs').text('');
    $('#result_others').text('');
    $("#summery_table").find("tr:not(:first)").remove();
    $(".hidden_links").hide();
    $("#submit").prop("disabled", true);
  }

  init();

  var socket = io.connect($SCRIPT_ROOT);
  var input_url = $('#input_url').val();
  var server_ip = $('#server_ip').val();
  var req_header = $('#req_header').val();

  socket.emit('log_diver', { 
    'input_url': encodeURI(input_url),
    'server_ip': server_ip,
    'req_header': req_header 
  });

  socket.on('log_diver', function(message) {
    var json = jQuery.parseJSON(message);

    if (json.type == "request") {
      $('#console').append('[Request Header]\n' + json.content)
    } else if (json.type == "response") {
      $('#result_response_header').text(json.content);
    } else if(json.type == "console") {
      $('#console').append(json.content);
      $('#console').scrollTop($('#console')[0].scrollHeight);
    } else if(json.type == "progress") {
      progressLogdiver = json.content.trim();
      if (progressLogdiver >= 100) {
        window.clearInterval(progressVar);
        $('#progress_bar').attr('style', 'width: 100%');
      }
    } else if(json.type == "error") {
        window.clearInterval(progressVar);
        init();
        $('#progress_bar').addClass('progress-bar-warning');
        $('#progress_bar').attr('style', 'width: 100%');
        $('#console').append(json.message);
        $('#input_url').focus().select();
        $("#submit").prop("disabled", false);
        
    } else if(json.type == "log") {
      $('.result_logs').append(json.content.trim());
      $('.hidden_links').show();
      $('#result_others').append(json.others.trim());
      $("#googlemap").attr("src", "/googlemap?google_maps=" + json.summery);
      
      var summery = JSON.parse(json.summery.replace(/'/g, "\""));

      for(i = 1; i < summery.length; i++) {
        $("#summery_table").append(
        '<tr><td>' + summery[i][0] + '</td><td>' + summery[i][4] + '</td><td>' + summery[i][5] + '</td><td>' + summery[i][6] + '</td><td>' + summery[i][7] + '</td><td>' + summery[i][3] + '</td></tr>');
        }

      $("#submit").prop("disabled", false);
      $('#input_url').focus();
    }
  });

  socket.on('disconnect', function() {
    progress = 1;
    progressLogdiver = 0;
    window.clearInterval(progressVar);
  });
});  