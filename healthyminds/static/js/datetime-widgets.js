/* Initialize functions for JQueryUI Datepicker and jquery-timepicker */

$(document).ready(function(){
	setup_widgets();
});

function assign_value(value, default_value){
	return value != undefined ? value : default_value;
}

function setup_widgets(){
	var static_url = '/static/'; //get_url('static');
	if(typeof(static_url) == "undefined"){
		setTimeout(function(){
			setup_widgets();
		}, 100);
		return;
	}
	$.datepicker.setDefaults({ showOn: "both", prevText:'&laquo;', nextText:'&raquo',
		buttonImageOnly: true, buttonText: "", buttonImage: [static_url,"img/calendar-icon.png"].join(''),});

	initialize_datetime_widget();
}

function initialize_datetime_widget(){
    var datepickers = initalize_datepicker();
    var timepickers = initialize_timepicker();
    var widget_class = "datetime-widget";
    var datepicker_wrapper_selector = ".datepicker-wrapper";
    widget_wrapper = ['<div class=',widget_class,'>'].join('"');
    datepickers.not(['.',widget_class,' ', datepicker_wrapper_selector ].join('')).each(function(){
        var datepicker = $(this).closest(datepicker_wrapper_selector);
        var next = datepicker.next();
        if(next.hasClass("timepicker-wrapper")){
            $(datepicker).add(next).wrapAll(widget_wrapper);
        }
    });
}

function initialize_timepicker(selector_class){
    var has_timepicker_selector = '.ui-timepicker-input';
    var timepicker_wrapper = "<div class='timepicker-wrapper'>";
    var selector = [".",assign_value(selector_class, 'timepicker')].join("");
    var timepicker_label = "<span class='timepicker-label'>at</span>";
    var timepickers = $(selector).not(has_timepicker_selector).wrap(timepicker_wrapper).timepicker(
    		{ 'timeFormat': 'G:i A' , 'scrollDefault': 'now' });
    timepickers.timepicker('option', {'timeFormat': 'g:i A' });
    timepickers.each(function(){$(this).change();});
    $('.datetime-widget', selector).before(timepicker_label);
    return timepickers;
}

function initalize_datepicker(selector_class){
	var has_datepicker_selector = '.hasDatepicker';
	var datepicker_wrapper = '<div class="datepicker-wrapper">';
	var selector = "."+assign_value(selector_class, 'datepicker');
	return $(selector).not(has_datepicker_selector).wrap(datepicker_wrapper).datepicker();
}
