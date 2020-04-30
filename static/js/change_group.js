let form = document.querySelector('#change-group');
form.addEventListener('submit', async function (ev) {
    ev.preventDefault();
    let oData = new FormData(form);
    let text = '';
    side = window.location.href.includes('student') ? 'student' : 'alum';
    url = `/${side}/id`;
    try {
        let response = await fetch(url, {
            body: oData,
            method: 'post'
        });
        response = await response.json();
        if (response.changed) {
            console.log(response.id);
            $('.id-display').html(response.id);
            $('#staticId').val(response.id);
        }
        text = response.msg;
    } catch {
        text = 'An unexpected error occurred';
    }
    alert(text);
    $('#exampleModal').modal('toggle');
    $('#id').val('');
});