<<<<<<< HEAD
let form = $('#action-form');
let action = $('#action-select');
let selectedUsers = $('#checked-members');

action.on('input', () => {
    function reset() {
        action.val('no-action');
        // action.html('Select an action');
    }
    let answer = confirm(`Are you sure you would like to ${action.val()} the selected users?`);
    if (!answer) {
        reset();
        return;
    }
    if (!selectedUsers.val()) {
        reset();
        alert('No users were selected');
        return;
    }
    form.submit();
=======
let form = $('#action-form');
let action = $('#action-select');
let selectedUsers = $('#checked-members');
let selectAll = $('#select-all');

action.on('input', () => {
    function reset() {
        action.val('no-action');
        // action.html('Select an action');
    }
    let answer = confirm(`Are you sure you would like to ${action.val()} the selected users?`);
    if (!answer) {
        reset();
        return;
    }
    if (!selectedUsers.val()) {
        reset();
        alert('No users were selected');
        return;
    }
    form.submit();
>>>>>>> master
});