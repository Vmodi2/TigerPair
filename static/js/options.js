$(document).ready(() => {
    update_majors();
    update_careers();
});

function update_careers() {
    careers = ["Accounting", "Advertising", "Architecture/Planning", "Building/Construction", "Care-Physical", "Consulting", "Energy Resources", "Engr-Chemical", "Engr-Civil", "Engr-Electrical", "Engr-Mech/Aerospace", "Engr-Other", "Environmental Affairs", "Fin-Asset Management", "Fin-Corporate Finance", "Fin-Financial Planning", "Fin-Hedge Funds", "Fin-Investestment Banking", "Fin-Investment Management", "Fin-Private Equity", "Finance-Commercial Banking", "Finance-Other", "Finance-Securities/Commodities", "Finance-Tax", "Finance-Venture Capital", "Foreign Service", "Fundraising", "Gov-Cabinet Member", "Gov-Executive", "Gov-Legislator", "Gov-Other", "Gov-Policy Analysis", "Gov-Politics", "Gov-White House Staff", "Health Care-Mental", "Health Care-Other", "Health", "Human", "Insurance", "Law-Corporate", "Law-Criminal", "Law-Intellectual Property", "Law-Litigation", "Law-Other", "Law-Patent/Copyright", "Law-Tax", "Law-Trusts and Estates", "Marketing", "Military", "Other", "Performing Arts", "Printing/Publishing", "Public Relations", "Radio/TV/Film/Theater", "Real Estate", "Religious Services", "Research & Development", "Resources", "Sales", "Social Work", "Sports/Recreation", "Teaching-Arts", "Teaching-Humanities", "Teaching-Other", "Teaching-Science/Engr", "Teaching-Social Science", "Tech-Biotechnology", "Tech-E-Commerce", "Tech-Hardware", "Tech-Information Services/Systems", "Tech-Software Dev", "Tech-Telecommunications", "Technology-Other", "Transportation/Travel", "Trust & Estate", "Veterinary Medicine", "Visual/Fine Arts", "Writing/Editing"];

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
