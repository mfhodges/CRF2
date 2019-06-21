from library import *


#################################
##### a lil testing for the #####
##### Open Data API wrapper #####
#################################
#print(">> ")

OpenData = OpenData()

"""
print(">>  OpenData.get_available_terms()")
print(OpenData.get_available_terms())
input("Press Enter to continue...\n")

print(">> OpenData.call_api(result_data=True)")
OpenData.set_uri('course_info/ACCT/')
print(OpenData.call_api(result_data=True))
input("Press Enter to continue...\n")

print(">> OpenData.call_api(result_data=False)")
print(OpenData.call_api(result_data=False))
input("Press Enter to continue...\n")

print(">> OpenData.next_page()")
print(OpenData.next_page())
input("Press Enter to continue...\n")

print(">> OpenData.next_page()")
print(OpenData.next_page())
input("Press Enter to continue...\n")

print(">> OpenData.next_page()")
print(OpenData.next_page())
input("Press Enter to continue...\n")

print(">> OpenData.next_page()")
print(OpenData.next_page())
input("Press Enter to continue...\n")
"""
#print(">> OpenData.get_courses_by_term(term1)")
OpenData.clear_settings()
terms = OpenData.get_available_terms()
term1 = terms[0]
OpenData.clear_settings()
print(">> OpenData.get_courses_by_term(term1)")
print(OpenData.get_courses_by_term(term1))
input("Press Enter to continue...\n")



# 'name': 'Elizabeth Shank', 'penn_id': '10124627'



#OpenData.set_uri('directory_person_details/89450759')
#print(OpenData.call_api())
#input("Press Enter to continue...\n")
