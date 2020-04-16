function update_majors() {
	majors = [	"AAS", "ANT", "ARC", "ART", "AST", "CBE", "CEE", "CHM", "CLA", "COM", "COS", "EAS",
				"ECO", "EEB", "ELE", "ENG", "FRE", "GEO", "GER", "HIS", "MAE", "MAT", "MOL", "MUS",
				"NES", "NEU", "ORF", "PHI", "PHY", "POL", "PSY", "REL", "SLA", "SOC", "SPO", "WWS" ];

	major_string = '<option value="{{major}}" selected hidden>{{major}}</option>';
	for (var i = 0; i < majors.length; i++) {
		major = majors[i];
		major_string += '<option value="' + major.toLowerCase() + '">' + major + '</option>';
	}
	
	major_string += '<option value="other">Other</option>'
	
	document.getElementById("major").innerHTML = major_string;
}