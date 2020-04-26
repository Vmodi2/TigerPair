$('.edit-btn').on('click', () => {
    $("#firstname").attr('readOnly', false);
    $("#lastname").attr('readOnly', false);
    $("#email").attr('readOnly', false);
    $("#major").attr('disabled', false);
    $("#career").attr('disabled', false);
    $(".edit-btn").attr('hidden', true);
    $("#submit").attr('hidden', false);
});