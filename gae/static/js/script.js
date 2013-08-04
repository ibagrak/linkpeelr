/* Author: @ibagrak */
var headline_count;
var headline_interval;
var current_headline = 0;
var old_headline = 0;
var max_rotations = 500;

$(document).ready( function() {
    

    // remove ugly IE shadow around links / tabs
    $("a").focus(function() { $(this).blur(); });

    // attach datepicker fields
    $('div[id$="datepicker"]').datepicker();

    // enable tabs on the index page
    $('#tabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });

    // setup validation to play well with default Twitter bootstrap classes
    $('form').each(function () {
        $(this).validate({
            errorClass:     "error",
            errorElement:   "span", // class='help-inline'

            highlight: function(element, errorClass, validClass) {
                if (element.type === 'radio') {
                    this.findByName(element.name).parent("div").parent("div").removeClass(validClass).addClass(errorClass);
                } else {
                    $(element).parent("div").parent("div").removeClass(validClass).addClass(errorClass);
                }
            },
            unhighlight: function(element, errorClass, validClass) {
                if (element.type === 'radio') {
                    this.findByName(element.name).parent("div").parent("div").removeClass(errorClass).addClass(validClass);
                } else {
                    $(element).parent("div").parent("div").removeClass(errorClass).addClass(validClass);
                }
            }
        });
    });

    headline_count = $("div.headline").size();
    $("div.headline:eq(" + current_headline + ")").css('top', '0px');
    
    headline_interval = setInterval(rotate_headline, 3000);
    $('#test_scroller').hover(function() {
        clearInterval(headline_interval);
    }, function() {
        headline_interval = setInterval(rotate_headline, 3000);
        rotate_headline();
    });

    function animate_headline(current_headline, old_headline) {
        $("div.headline:eq(" + old_headline + ")").animate({"top": "-95px"}, "slow", function() {
             $(this).css('top', '95px');
        });
        
        $("div.headline:eq(" + current_headline + ")").animate({"top": "0px"}, "slow", function() {
            
        });
    }

    function set_headline(current_headline, message, key) {
        $("div.headline:eq(" + current_headline + ")").html(message);
        $("div.headline:eq(" + current_headline + ")").removeClass('empty');

        if (key) {
            $("div.headline:eq(" + current_headline + ")").attr('id', key)
        }
    }

    function rotate_headline() {
        current_headline = (old_headline + 1) % headline_count;
        max_rotations = max_rotations - 1;
        
        // prevent infinite API call if they leave the webpage loaded for a long time
        if (max_rotations < 0) {
            $("div.headline:eq(" + old_headline + ")").animate({top: -95},"slow", function() {
                $(this).css('top', '95px');
            });
        
            $("div.headline:eq(" + current_headline + ")").animate({top: 0},"slow");

            old_headline = current_headline;
            return;
        }

        $.ajax({
            type: 'GET',
            url: '/rpc/last',
        }).done(function(data, code, jqxhr) {
            var code = data['code'];
            var message = data['response'];
                
            if (code == 200) {  
                var exists = false;
                var key = message['time'];

                $(".headline").each(function(index) {
                    if ($(this).attr("id") == key) {
                        exists = true;
                    } 
                });
                
                if (!exists) {
                    var unpeeled = message['unpeeled']; 
                    var peeled = message['peeled']; 
                    var where = message['where']; 
                    var ip = message['ip']; 
                    
                    var ellipses = "";
                    
                    if (peeled.length > 50) {
                        ellipses = "...";
                    }
                    
                    var img_frag; 
                        if (ip != '127.0.0.1') {
                            img_frag = '<img style="vertical-align:text-top" height="12px" src="http://api.hostip.info/flag.php?ip=' + ip + '>';
                        } else {
                            img_frag = 'localhost'
                        }

                    var html_code = '<span class="from" style="font-size:small"><a href="' + unpeeled + '">' + unpeeled + '</a></span> <br> \
                            &dArr;<br> \
                            <span class="to"><a href="' + peeled + '">' + peeled.substr(0,50) + ellipses + '</a></span><br> \
                            <div id="peeled_info">peeled while browsing <em>' + where + '</em> in ' + img_frag + '</div>'

                    set_headline(current_headline, html_code, key);
                }
            }      
        }).fail(function(jqxhr, code, exception) {
            // TODO: Error handling
            var data = $.parseJSON(jqxhr.responseText);
            var code = data['code'];
            var message = data['message'];
            
            if (code == 402) {
                set_headline(current_headline, 'Looks like nobody is peeling anything at the moment.', null);
            } else {
                set_headline(current_headline, 'An error has occurred!', null);
            }
            
        }); 

        animate_headline(current_headline, old_headline); 
        old_headline = current_headline;   
    };
});
