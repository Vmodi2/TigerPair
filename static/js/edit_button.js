function edit() {
	document.getElementById("firstname").readOnly = false;
	document.getElementById("lastname").readOnly = false;
	document.getElementById("email").readOnly = false;
	document.getElementById("major").disabled = false;
	document.getElementById("career").disabled = false;
	document.getElementById("edit").hidden = true;
	document.getElementById("submit").hidden = false;
}