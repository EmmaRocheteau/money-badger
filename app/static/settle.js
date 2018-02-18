// Comment
var main = function() {
    $('.settle').click(function() {
        $(this).toggleClass("btn-primary btn-success");
        $(this).parent().parent().hide(1000);
        console.log($(this).attr("nm"))
        $.getJSON('/home/remove_debtor', {
            nm: $(this).attr("nm")
        }, function(data){

        });
    });

    $('.settle-all').click(function(){
        $('.settle').parent().parent().hide(1000);
    });
}

$(document).ready(main);