$(document).ready(() => {
    function initialize(button, image) {
        button.on('mouseover', () => {
            image.addClass('miniBounce');
            setTimeout((() => {
                image.removeClass('miniBounce');
            }), 1000);
        });
    }
    initialize($('#littletiger-btn'), $('#littletiger-img'));
    initialize($('#bigtiger-btn'), $('#bigtiger-img'));

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