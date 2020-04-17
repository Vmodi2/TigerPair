function update_careers() {
	careers = ["Accounting", "Advertising", "Architecture/Planning", "Building/Construction", "Consulting",
		"Energy", "Engr.-Chemical", "Engr.-Civil", "Engr.-Electrical", "Engr.-Mech./AerospaceEngr.",
		"Engr-Other", "Environmental Affairs", "Finance", "Health care"];

	career_menu = document.getElementById("career");
	for (var i = 0; i < careers.length; i++) {
		option = document.createElement("option");
		option.value = careers[i];
		option.innerHTML = careers[i];
		career_menu.appendChild(option);
	}
}