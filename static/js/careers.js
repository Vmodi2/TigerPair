function update_careers() {
	careers = ["Accounting", "Advertising", "Architecture/Planning", "Building/Construction", "Consulting", 
	"Energy", "Engr.-Chemical", "Engr.-Civil", "Engr.-Electrical", "Engr.-Mech./AerospaceEngr.", 
	"Engr-Other", "Environmental Affairs", "Finance", "Health-Care"];

	career_string = document.getElementById("career").innerHTML;
	for (var i = 0; i < careers.length; i++) {
		career = careers[i];
		career_string += '<option value="' + career + '">' + career + '</option>';
	}

	document.getElementById("career").innerHTML = career_string;
}