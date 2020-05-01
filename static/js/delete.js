$('.members').on('change', () => {
    let checked = Array.prototype.slice.call(document.querySelectorAll('.members:checked')).map(function (el) {
        return el.value;
    }).join(',');
    $('#checked-members').val(checked);
});