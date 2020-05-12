let a = document.querySelector('#delete-account');
a.addEventListener('click', function (ev) {
    ev.preventDefault();
    let response = confirm('Are you sure you would like to permanently delete this account?');
    if (response) {
        window.location.assign($(a).attr('href'));
    }
});