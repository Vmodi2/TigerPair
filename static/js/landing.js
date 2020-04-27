$(document).ready(() => {
    function initialize(button, image) {
        button.on('mouseover', () => {
            // image.removeClass('miniBounceDown');
            image.addClass('move-up');
        });
        button.on('mouseout', () => {
            // image.removeClass('miniBounceUp');
            image.removeClass('move-up');
        });
    }
    initialize($('#student-btn'), $('#littletiger-img'));
    initialize($('#alum-btn'), $('#bigtiger-img'));

    let myNav = $('#landing-nav');
    $(window).on('scroll', () => {
        "use strict";
        if ($(document).scrollTop() >= 200) {
            myNav.removeClass("transparent", 5000);
        }
        else {
            myNav.addClass("transparent", 5000);
        }
    });



});


