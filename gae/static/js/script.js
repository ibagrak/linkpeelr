/* Author: @ibagrak */
var headline_count;
var headline_interval;
var current_headline = 0;
var old_headline = 0;
var max_rotations = 500;

$(document).ready( function() {
    
    // remove ugly IE shadow around links / tabs
    $("a").focus(function() { $(this).blur(); });

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

    /* 
    REST API CRUD forms
    */

    // helpers
    var restore = function(frm) {
        // Restore
        // only restore children inputs of controls or checkboxes (doesn't apply to datepicker)
        frm.find('.controls > :input').removeAttr('disabled');
        frm.find('.controls > :input').val('');
        frm.find('.checkbox > :input').removeAttr('disabled');
        frm.find(':button').each(function() {
            $(this).removeAttr('disabled');
        });
    };
            
    var show_result = function(result, msg) {
        // hide form & show result
        result.html(msg);
        result.show();
        result.fadeOut(3000);
    };

    // 1. online peeler
    $('#peel_btn, #follow_btn').click(function () {
        var btn = $(this);
        var frm = $(this).parents('form');
        var result = $(this).siblings('.form_result');
        var kvs = {}
        var invalid_fields = false;
        var action = $(this).attr('name');

        if (action == 'follow') {
            if ($("#url").val() != '') {
                window.location = $("#url").val()
            }
            return false;
        }

        frm.find(":input").each(function() {
            if (!$(this).hasClass('dp') && !$(this).hasClass('checkbox') && !frm.validate().element($(this)))
                invalid_fields = true;

            if ($(this).attr('type') == 'password') {
                kvs[$(this).attr('id')] = MD5($(this).val());
            } else {
                kvs[$(this).attr('id')] = $(this).val();
            }
        });

        if (invalid_fields) 
            return false;

        if (kvs['url'] == '') {
            show_result(result, 'Enter a valid URL')
            return false;
        }

        // from mustache template
        kvs['version'] = "2.1.0";
        kvs['where'] = "http://localhost:8086";

        // Disable form
        frm.find(':input').attr('disabled', '');
        
        // Disable button
        btn.attr('disabled', '');
        
        $.ajax({
            type: 'GET',
            url: '/rpc/' + action,
            data: kvs,
        }).done(function(data, code, jqxhr) {
            var code = data['code'];
            var message = data['response'];

            // Restore
            restore(frm, btn);
                
            if (code == 301 || code == 302) {  
                frm.find("#url").val(message['url'])
            } else {
                frm.find("#url").val(kvs['url'])
            }          
        }).fail(function(jqxhr, code, exception) {
            // TODO: Error handling
            var data = $.parseJSON(jqxhr.responseText);
            var code = data['code'];
            var message = data['response'];
            
            // Restore
            restore(frm, btn);
            
            show_result(result, 'Oops! Something is wrong.');
        }); 
    });

    // 3. scroller
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
            } else if (code == 402) {
                set_headline(current_headline, 'Looks like nobody is peeling anything at the moment.', null);
            }     
        }).fail(function(jqxhr, code, exception) {
            set_headline(current_headline, 'An error has occurred!', null);
        }); 

        animate_headline(current_headline, old_headline); 
        old_headline = current_headline;   
    };
});
