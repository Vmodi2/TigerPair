let form = document.querySelector('#changeaccount')
form.addEventListener('submit', async function(ev) {
  ev.preventDefault()
  let response = confirm('Are you sure you would like to permanently transfer ownership of this account?')
  if response {
  let formData = new FormData(form)
  try {
  await fetch('/admin/change', {
    method: 'post',
    body: formData
  });
} catch {
  alert('fsdfsdfsdf')
}
}
else {
  alert('they clicked cancel')
}
);
