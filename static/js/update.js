// $('[id^=edit-btn]').on('click', function () {
//     $("#firstname").attr('readOnly', false);
//     $("#lastname").attr('readOnly', false);
//     $("#email").attr('readOnly', false);
//     $("#major").attr('disabled', false);
//     $("#career").attr('disabled', false);
//     $(this).attr('hidden', true);
//     $(this).next().attr('hidden', false);
// });


$('#edit-btn-1').on('click', function () {
    $("#firstname").attr('readOnly', false);
    $("#lastname").attr('readOnly', false);
    $("#email").attr('readOnly', false);
    $("#major").attr('disabled', false);
    $("#career").attr('disabled', false);
    $(this).attr('hidden', true);
    $(this).next().attr('hidden', false);
});

$('#edit-btn-2').on('click', function () {
    $("#info-1").attr('readOnly', false);
    $("#info-2").attr('readOnly', false);
    $("#info-3").attr('readOnly', false);
    $("#info-4").attr('disabled', false);
    $(this).attr('hidden', true);
    $(this).next().attr('hidden', false);
});