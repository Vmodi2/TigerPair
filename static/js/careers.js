function update_career() {
	career = ['Accounting', 'Advertising', 'Architecture/Planning', 'Building/Construction', 'Consulting', 
	'Energy', 'Resources', 'Engr.-Chemical', 'Engr.-Civil', 'Engr.-Electrical', 'Engr.-Mech./AerospaceEngr.', 
	'Engr-Other', 'Environmental Affairs', 'Finance', 'Health-Care'];

	career_string = document.getElementById("career").innerHTML;
	for (var i = 0; i < career.length; i++) {
		career = career[i];
		career_string += '<option value="' + career.toLowerCase() + '">' + career + '</option>';
	}

	career_string += '<option value="other">Other</option>'

	document.getElementById("career").innerHTML = career_string;
}