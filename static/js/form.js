$(document).ready(() => {
    update_majors();
    update_careers();
});
$('.edit-btn').on('click', () => {
    $("#firstname").attr('readOnly', false);
    $("#lastname").attr('readOnly', false);
    $("#email").attr('readOnly', false);
    $("#major").attr('disabled', false);
    $("#career").attr('disabled', false);
    $(".edit-btn").attr('hidden', true);
    $("#submit").attr('hidden', false);
});

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

function update_majors() {
    majors = ["AAS", "ANT", "ARC", "ART", "AST", "CBE", "CEE", "CHM", "CLA", "COM", "COS", "EAS",
        "ECO", "EEB", "ELE", "ENG", "FRE", "GEO", "GER", "HIS", "MAE", "MAT", "MOL", "MUS",
        "NES", "NEU", "ORF", "PHI", "PHY", "POL", "PSY", "REL", "SLA", "SOC", "SPO", "WWS"];

    major_string = document.getElementById("major").innerHTML;
    for (var i = 0; i < majors.length; i++) {
        major = majors[i];
        major_string += '<option value="' + major + '">' + major + '</option>';
    }

    /* major_string += '<option value="XXX">Other</option>'; */

    document.getElementById("major").innerHTML = major_string;
}