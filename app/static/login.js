// root.js

var main = function() {
    $(".form").submit(function(event){
    event.preventDefault();
     $(".gif").show();
     this.submit(); //now submit the form
    });

}

$(document).ready(main);