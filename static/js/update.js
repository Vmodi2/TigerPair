toggle = function (className) {
    return function () {
        $(className).attr('readonly', false);
        $(className).attr('disabled', false);
        $(this).attr('hidden', true);
        $(this).next().attr('hidden', false);
        console.log(obj);
    };
};

$('#edit-btn-1').on('click', toggle('.info-1'));
$('#edit-btn-2').on('click', toggle('.info-2'));