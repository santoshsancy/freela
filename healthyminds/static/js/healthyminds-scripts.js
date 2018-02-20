function capitaliseFirstLetter(string){return string.charAt(0).toUpperCase() + string.slice(1);}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function mkstr(text, strargs){
	strargs = strargs.reverse();
	return text.replace(/%s/g, function(x){return strargs.pop()});
}

function rounder(value, decimals){
	var shift = 10 * decimals;
	return Math.round(value * shift)/shift;
}

function exists(value){
	return value != undefined && typeof(value) !== "undefined";
}

function assign_value(value, default_value){
	return value != undefined ? value : default_value;
}

$.fn.animateRotate = function(startAngle, endAngle, duration, easing, complete) {
    var args = $.speed(duration, easing, complete);
    var step = args.step;
    return this.each(function(i, e) {
        args.step = function(now) {
            $.style(e, 'transform', 'rotate(' + now + 'deg)');
            if (step) return step.apply(this, arguments);
        };
        $({deg: startAngle}).animate({deg: endAngle}, args);
    });
};

$(document).ready(function(){
	FastClick.attach(document.body);
	$.mobile = (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase()));
	if($.mobile){}

	$('.nav-toggle').click(function(){
		var bod = $('body');
		var active_classname = 'sidepanel-open';
		if(bod.hasClass(active_classname)){
			bod.removeClass(active_classname);
		}else{
			bod.addClass(active_classname);
		}
	});

	if(typeof($(window).scrollTo) != "undefined"){
		$(document).on('click', '[data-scroll-target]', function(){
			$(window).scrollTo($(this).attr('data-scroll-target'), 400, {offset:{top:-$('.navbar-wrapper').outerHeight()}});
		});
	}

	/* MTS FUNCTIONS */
	$('.survey_matrix').add('.range').each(function(){
		var me=$(this);
		me.addClass("span"+me.find('tr').first().children().length);
	});

	$('input[type=radio]').click(function(){
		var me = $(this);
		var groupname = me.attr('name');
		try{ var group = $('input[type=radio][name='+groupname+']'); }
		catch(e){ var group = $('input[type=radio]'); }
		$(group).parent().removeClass('checked');
		$(this).parent().addClass('checked');
	});

	$('input[type=checkbox]').click(function(){
		var me = $(this);
		if(me.prop('checked')){
			me.parent().addClass('checked');
		}else{
			me.parent().removeClass('checked');
		}
	});
	// Applies checked styling to existing selections on pageload //
	$('input:checked').add("input[checked=checked]").each(function(){ $(this).closest('label').addClass('checked'); });
	$("option[value=Other]").closest('select').each(function(){
        var me=$(this);
        var other= $('input[name='+me.attr('name')+'Other]');
        if(other.length > 0){
            me.attr("other-target",other.attr('name'));
            if(me.val() != "Other" ){
            	other.parent().addClass('hidden');
            }
            me.change(function(){
                var other = $("input[name="+$(this).attr('other-target')+"]").parent();
                if($(this).val() != "Other" ){
                }else{other.removeClass('hidden').css('display','none');
                other.fadeIn();}
            });
        }
    });

	$('audio').on('play', function(){
        var me = $(this);
        record_event("AudioPlay", me.currentSrc);
    });
    $('video').on('play', function(){
        var me = $(this);
        record_event("VideoPlay", me.currentSrc);
    });

    $('audio').on('pause', function(){
        var me = $(this);
        record_event("AudioPause", me.currentSrc);
    });
    $('video').on('pause', function(){
        var me = $(this);
        record_event("VideoPause", me.currentSrc);
    });

    $('audio').on('ended', function(){
        var me = $(this);
        record_event("AudioCompleted", me.currentSrc);
    });

    $('video').on('ended', function(){
        var me = $(this);
        record_event("VideoCompleted", me.currentSrc);
    });

    $('.file-controller input[type=file]').on('change', handle_file_select);
    $('[data-load]').each(function(){
    	var me = $(this);
    	me.html(get_loading_indicator());
    	ajaxReplace(me, me.data('load'));
    });
});


function frame_resize(){
	var frames = $('iframe');
	if (typeof frames.iFrameResize === "function") {
		frames.iFrameResize({heightCalculationMethod:'taggedElement'});
		$(window).focus();
	}
}

function ajaxReplace(elem, url){
	$.ajax({url:url, datatype: 'html',
		success : function(data) {
			elem.replaceWith(data);
	  },error : function(data) {
		 console.log(data.responseText);
	  }
	});
}

function class_str(classname){
	return "."+classname;
}

function class_elem(elem, classname, text, closetag){
	closestring = closetag == true ? elem : "";
	text =  assign_value(text,"");
	return mkstr("<%s class='%s'>%s</%s>",[elem,classname,text,closestring]);
}

function close_modal(){
	$('.backdrop').add('.modal').remove();
}

function init_fetch_modal(){
	var init_class = 'fetch-modal-initialized';

	$('.fetch-modal').not(class_str(init_class)).on('click', function(){
		if($('.modal').length < 1){
			build_modal(this);
		}
	}).addClass(init_class);
}

function init_close_modal(){
	$('.backdrop').add('[data-action=modal-hide]').click(close_modal);
}

function fetch_modal(elem){
	var me = $(elem);
	var url = me.data('src');
	$.ajax({url:url,
			success:function(data){
				$('body').append(data);},
			error:function(data){
				console.log(data.ResponseText);}
	});
}

function build_modal(elem){
	var me = $(elem);
	var modal_url = me.data('src');
	modal_constructor(modal_url);
}

function url_modal(modal_url){
	modal_constructor(modal_url);
}

function modal_constructor(modal_url){
	var html = '<div class="modal object-frame"></div><div class="backdrop"></div>';
	$('body').append(html);
	$('.backdrop').click(close_modal);
	$('.modal').html(get_loading_indicator());
	$('.modal').css('top', window.scrollY+20);
	$.ajax({url:modal_url,
			success:function(data){
				$('.modal').replaceWith(data);
				$( ".accordion" ).accordion({
					active: false,
					collapsible: true,
					heightStyle: "content"
				});
				position_modal();
				init_close_modal();
				frame_resize();
			},error:function(data){
				console.log(data.ResponseText);}
	});
}

function position_modal(){
	var modal = $('.modal');
	if(modal.height() < $(window).height()){
		modal.css('position', 'fixed');
	}else{
		modal.css('top',window.scrollY+20);
	}
}

function get_dimensions(elem){
    var item = $(elem);
    var display = item.css('display');
    var current_vals = {width: item.width(), height: item.height(), outerheight: item.outerHeight(), outerwidth: item.outerWidth()};
    item.css({"display":"block","height":"auto",'width':"auto"});
    var obj = {width:item.width(),height:item.height(),outerheight:item.outerHeight(),outerwidth:item.outerWidth()};
    item.css('display',display);
    return obj;
}

function record_event(type, note, uid){
	$.ajax({url: get_url('record-event'), datatype: 'html', data: {type:type, note:note, uid:uid},
		success : function(data) {}, error : function(data) {console.log(data);}
	});
}

function backdrop_html(additional_classname){
	return mkstr("<div class='backdrop %s'></div>", [assign_value(additional_classname, "")]);
}

function videoplayer(key){
	var html = "<div class='modal-backdrop'></div>";
	$('.modal.'+key).removeClass('hidden');
	$('.wrapper').append(html);
	$('.modal-backdrop').add('.modal .close').click(function(){
		$('.modal').addClass('hidden');
		$('.modal-backdrop').remove();
		$('video').each(function(){ this.pause();});
	});
	record_event('VideoOpened',key);
}

function fetch_glossary(term){
	$.ajax({url:'/glossary-item/',datatype: 'html',
		  data: {term:term},
		  success : function(data) {
			 $('.glossary-box').html(data);
			 $('.glossary-wrapper').fadeIn();
		  },
		  error : function(data) {
			 console.log(data.responseText);
		  }
    });
}

function fetch_panel(url){
	$.ajax({url:url,data:{},
		  success:function(data){
			 $('.info-panel').replaceWith(data);
		  },error:function(data){},
	});
}

function close_frame(){
	$('iframe.tutorial-frame').add('.instruction-backdrop').fadeOut(400, function(){
		$(this).remove();
	});
}

function toggle_class(elem, classname){
	var e=$(elem);
	if(e.hasClass(classname)){e.removeClass(classname);
	}else{e.addClass(classname);}
}

function hide_or_show(classname){
	hidden = $('.'+classname).filter('.hidden');
	shown =  $('.'+classname).not('.hidden');
	hidden.removeClass('hidden');
	shown.addClass('hidden');
}

function match_height(el1, el2){
	var h1 = $(el1).height();
	var h2 = $(el2).height();
	if(h1 > h2){ $(el2).height(h1);}
	else{ $(el1).height(h2);}
}

function get_loading_indicator(){
	return class_elem('div','loading-indicator','Loading',true);
}

function handle_file_select(){
    var me = $(this);
    var controller = me.closest('.file-controller');
    var thumb = $(me.attr('data-image-target'));
    var files = this.files;
    console.log(controller, thumb, files);
    // Loop through the FileList and render image files as thumbnails.
    for (var i = 0, f; f = files[i]; i++) {
      // Only process image files.
      if (!f.type.match('image.*')) {
        continue;
      }
      var reader = new FileReader();
      // Closure to capture the file information.
      reader.onload = (function(theFile) {
        return function(e) {
          // Render thumbnail.
          thumb.attr('src',e.target.result);
        };
      })(f);
      // Read in the image file as a data URL.
      reader.readAsDataURL(f);
    }
}

function file_preview(evt){
	var f = evt.target.files[0]; // FileList object
	var reader = new FileReader();

    // Closure to capture the file information.
    reader.onload = (function(theFile) {
      return function(e) {
        // Render thumbnail.
        var span = document.createElement('span');
        span.innerHTML = ['<img class="thumb" src="', e.target.result,
                          '" title="', escape(theFile.name), '"/>'].join('');
        document.getElementById('list').insertBefore(span, null);
      };
    })(f);
}
