toggleEdit = function (className) {
    return function () {
        $(className).attr('readonly', false);
        $(className).attr('disabled', false);
        $(this).attr('hidden', true);
        $(this).next().attr('hidden', false);
    };
};

$('#edit-btn-1').on('click', toggleEdit('.info-1'));
$('#edit-btn-2').on('click', toggleEdit('.info-2'));