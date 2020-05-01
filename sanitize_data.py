#!/usr/bin/env python

fields = 'Accounting Advertising Architecture/Planning Building/Construction Consulting Energy_Resources Engr-Chemical Engr-Civil Engr-Electrical Engr-Mech/Aerospace Engr-Other Environmental_Affairs Fin-Asset_Management Fin-Corporate_Finance Fin-Hedge_Funds Fin-Investment_Management Fin-Private_Equity Finance-Commercial_Banking Fin-Financial_Planning Fin-Investestment_Banking Finance-Other Finance-Securities/Commodities Finance-Tax, Trust_&_Estate Finance-Venture_Capital Foreign_Service Fundraising Gov-Cabinet_Member Gov-Executive Gov-Legislator Gov-Other Gov-Policy_Analysis Gov-Politics Gov-White_House_Staff Health_Care-Mental Health Care-Other Health Care-Physical Human Resources Insurance Law-Corporate Law-Criminal Law-Intellectual_Property Law-Litigation Law-Other Law-Patent/Copyright Law-Tax Law-Trusts_and_Estates Marketing Sales Military Performing_Arts Printing/Publishing Public_Relations Radio/TV/Film/Theater Real_Estate Religious_Services Research_&_Development Social_Work Sports/Recreation Teaching-Arts Teaching-Humanities Teaching-Other Teaching-Science/Engr Teaching-Social_Science Tech-Biotechnology Tech-E-Commerce Tech-Hardware Tech-Software_Dev Tech-Information_Services/Systems Tech-Telecommunications Technology-Other Transportation/Travel Veterinary_Medicine Visual/Fine_Arts Writing/Editing Other'

new_fields = fields.split(' ')
for i, field in enumerate(new_fields):
    if '.' in field:
        new_fields[i] = field.replace('_', ' ')
new_fields.sort()

f = open('fields.txt', 'w')
f.write(", ".join(new_fields))
f.close()
