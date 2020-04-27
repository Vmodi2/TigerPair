$('[id^=edit-btn]').on('click', function () {
    $("#firstname").attr('readOnly', false);
    $("#lastname").attr('readOnly', false);
    $("#email").attr('readOnly', false);
    $("#major").attr('disabled', false);
    $("#career").attr('disabled', false);
    $(this).attr('hidden', true);
    $(this).next().attr('hidden', false);
});