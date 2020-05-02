function update() {
    let checked = Array.prototype.slice.call(document.querySelectorAll('.members:checked')).map(function (el) {
        return el.value;
    }).join(',');
    $('#checked-members').val(checked);
}
$('.members').on('click', update);

$('#select-all').on('click', function () {
    $('.members').prop('checked', this.checked);
    update();
});