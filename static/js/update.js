toggleEdit = function (className, className2) {
    return function () {
        $(className).attr('readonly', false);
        $(className).attr('disabled', false);
        $(className).attr('hidden', false);
        $(className2).attr('hidden', true);
        $(this).attr('hidden', true);
        $(this).next().attr('hidden', false);
    };
};

$('#edit-btn-1').on('click', toggleEdit('.info-1','.current-info-1'));
$('#edit-btn-2').on('click', toggleEdit('.info-2','.current-info-2'));