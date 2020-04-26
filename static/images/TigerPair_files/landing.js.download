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
});