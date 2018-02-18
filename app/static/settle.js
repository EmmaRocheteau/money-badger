// Comment
var main = function() {
    $('.settle').click(function() {
        $(this).toggleClass("btn-primary btn-success");
        $(this).parent().parent().hide(1000);
        $.getJSON('/home/remove_debtor', {
            nm: $(this).closest(".nm").val(),
        }, function(data){

        });
    });

    $('.settle-all').click(function(){
        $('.settle').parent().parent().hide(1000);
    });
}

$(document).ready(main);