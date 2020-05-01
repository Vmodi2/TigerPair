$(document).ready(() => {
    update_majors();
    update_careers();
});
d
function update_careers() {
    careers = ["Accounting", "Advertising", "Architecture/Planning", "Building/Construction", "Car\
e-Other", "Care-Physical", "Consulting", "Energy Resources", "Engr-Chemical", "Engr\
-Civil", "Engr-Electrical", "Engr-Mech/Aerospace", "Engr-Other", "Environmental Aff\
airs", "Fin-Asset Management", "Fin-Corporate Finance", "Fin-Financial Planning", "\
Fin-Hedge Funds", "Fin-Investestment Banking", "Fin-Investment Management", "Fin-Pr\
ivate Equity", "Finance-Commercial Banking", "Finance-Other", "Finance-Securities/C\
ommodities", "Finance-Tax", "Finance-Venture Capital", "Foreign Service", "Fundrais\
ing", "Gov-Cabinet Member", "Gov-Executive", "Gov-Legislator", "Gov-Other", "Gov-Po\
licy Analysis", "Gov-Politics", "Gov-White House Staff", "Health Care-Mental", "Hea\
lth", "Health", "Human", "Insurance", "Law-Corporate", "Law-Criminal", "Law-Intelle\
ctual Property", "Law-Litigation", "Law-Other", "Law-Patent/Copyright", "Law-Tax", "\
Law-Trusts and Estates", "Marketing", "Military", "Other", "Performing Arts", "Pri\
nting/Publishing", "Public Relations", "Radio/TV/Film/Theater", "Real Estate", "Rel\
igious Services", "Research & Development", "Resources", "Sales", "Social Work", "S\
ports/Recreation", "Teaching-Arts", "Teaching-Humanities", "Teaching-Other", "Teach\
ing-Science/Engr", "Teaching-Social Science", "Tech-Biotechnology", "Tech-E-Commerc\
e", "Tech-Hardware", "Tech-Information Services/Systems", "Tech-Software Dev", "Tec\
h-Telecommunications", "Technology-Other", "Transportation/Travel", "Trust & Estate\
", "Veterinary Medicine", "Visual/Fine Arts", "Writing/Editing"]

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
