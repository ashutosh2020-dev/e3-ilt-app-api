import requests


def create_root_user():
    url = "http://middle-ilt-app.us-east-1.elasticbeanstalk.com/api/v1/other/root_user/?fname=ashutosh&lname=tiwari&email=at769773%40gmail.com&number=5121126&password=ajnjfn444&is_active=true&role_id=3"

    payload = {}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def create_school():
    school_name_list = ["school_A", "school_B", "school_C", "school_D"]
    payload = {}
    headers = {}
    for school_name in school_name_list:
        url = f"http://middle-ilt-app.us-east-1.elasticbeanstalk.com/api/v1/others/schools/?name={school_name}&location=k&district=k"
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
def create_role():
    role_name_list = ["member", "facilitator", "admin"]
    description = ["this is member", "this is facilitator", "this is admin"]
    for i in range(len(role_name_list)):
        url = f"http://middle-ilt-app.us-east-1.elasticbeanstalk.com/api/v1/others/roles/?role_name={role_name_list[i]}&roleDescription={description[i]}"
        payload = {}
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

create_role()
create_school()
create_root_user()