let a = document.querySelector('#clear-all');
a.addEventListener('click', function (ev) {
    ev.preventDefault();
    let response = confirm('Are you sure you would like to permanently clear all current matches?');
    if (response) {
        window.location.assign($(a).attr('href'));
    }
});