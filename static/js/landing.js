$(document).ready(() => {
    function initialize(button, image) {
        button.on('mouseover', () => {
            image.addClass('miniBounceUp');
            setTimeout((() => {
                image.removeClass('miniBounceUp');
            }), 1000);
        });
    }
    initialize($('#landing-btn-little'), $('#littletiger-img'));
    initialize($('#landing-btn-big'), $('#bigtiger-img'));

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