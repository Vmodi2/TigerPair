let form = document.querySelector('#change-account');
form.addEventListener('submit', function (ev) {
  ev.preventDefault();
  let response = confirm('Are you sure you would like to permanently transfer ownership of this account?');
  if (response) {
    form.submit();
  }
});