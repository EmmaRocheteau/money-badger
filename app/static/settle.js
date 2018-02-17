// Comment
var main = function() {
    $('.settle').click(function() {
      $(this).toggleClass("btn-primary btn-success");
      $(this).parent().parent().hide(1000);
    });

    $('.settle-all').click(function(){
        $('.settle').parent().parent().hide(1000);
    });
  }

  $(document).ready(main);