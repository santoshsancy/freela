var formset_object = initialize_formset('form');

$(document).ready(function(){
    $('.formset-block').on('click', '.btn-delete input', function(){
        var me = $(this);
        var answer_item = me.closest('.answer-block');

        if (answer_item.hasClass('deleted')) {
            answer_item.removeClass('deleted');
            $(answer_item).find('.hideable-element').show()
        }

        else {
            answer_item.addClass('deleted');
            $(answer_item).find('.hideable-element').hide();
        }
    });
});
