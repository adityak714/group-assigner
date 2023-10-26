##############################################################################################################
# Automate adding students from Canvas to a collection of group repositories on Gitlab
# Prerequisite:
# - Students fill in a survery, and send in their group number, and the Gitlab IDs of all of their co-members. 
# - Once a representative from every group has filled in that survey, download the students' answers in .csv
##############################################################################################################

import csv, requests, traceback
import subprocess, gitlab
import time, os
from dotenv import load_dotenv

start_time = time.time()
load_dotenv()

# Locating the file (assuming that it is saved in the same dir as this py script)
filename = "./Survey Group Registration Survey Student Analysis Report.csv"

try:
    # Iterating through each value, and subsequently each row in the csv.
    with open(filename, "r") as csvfile:
        datareader = csv.reader(csvfile, delimiter=",")
        next(datareader) # Skip the very first line in the csv, as that is the title line, for the columns.
        
        # This is executed per row, representing an answer received. At one iteration, the group of the specified number 
        # will be located in Gitlab, and the accounts of the mentioned IDs will be added to it with Moderator privileges.)
        for index, row in enumerate(datareader):

            # Assuming that the group number from an answer is stored in column 9 of the csv, or change based on how csv is generated.
            grp_num: str = str(row[9])
            # A list of members, that was first as a string, with each ID separated with commas as such: "XXXX,XXXX,XXXX"
            members: [int] = str(row[11]).split(sep=",")

            if (int(grp_num) < 10):
                grp_num = "0"+grp_num
            else:
                pass

            script = f'export gitlab_host=git@{os.getenv("GITLAB_HOST")} ;' + """
            mkdir assignment-grps ;
            cd assignment-grps ;
            """ + f'export project_name=a4-group-{grp_num} ;' + """ 
            mkdir "${project_name}" ;
            cd "${project_name}" ;
            git init ;
            git checkout -b main ;
            cp -r ../../a4-group-xx/* ../../a4-group-xx/.gitlab-ci.yml ../../a4-group-xx/.gitignore . ;
            git add . ;
            git commit -m "initial commit" ;
            git remote add origin "ssh://${gitlab_host}/courses/dit345/2023/groups/${project_name}.git" ;
            git push -u origin main
            """ + f'export test_repo=a4-group-{grp_num}-test ;' + """
            cd .. ; mkdir "${test_repo}" && cd "${test_repo}" ;
            git init ;
            git checkout -b main ;
            cp -r ../../a4-group-xx-test/* ../../a4-group-xx-test/.gitlab-ci.yml . ;
            git add . ;
            git commit -m "initial test commit" ; """ 
            + f'git remote add origin "ssh://${os.getenv("GITLAB_HOST")}/courses/dit345/2023/tests/$test_repo.git" ; git push -u origin main'
            
            p = subprocess.run(script, shell=True)
            # p = subprocess.run(["./sa-repo-init.sh", f'{int(grp_num)}'])

            if (p.returncode == 0):
                
                """
                **** CURL EQUIVALENT COMMAND: ****
                curl --request PUT --header "PRIVATE-TOKEN: {}" --data "name=main&developers_can_push=true&developers_can_merge=true" "https://{os.getenv("GITLAB_HOST")}/api/v4/projects/courses%2Fdit345%2F2023%2Fgroups%2Fa4-group-98/repository/branches/main/protect" | json_pp
                """

                ## Change privileges so that in a repo, both developers+maintainers can push/merge
                protected_branch = requests.put(f'https://{os.getenv("GITLAB_HOST")}/api/v4/projects/courses%2Fdit345%2F2023%2Fgroups%2Fa4-group-{grp_num}/repository/branches/main/protect', headers={
                    "PRIVATE-TOKEN": f'{os.getenv("PERSONAL_ACCESS_TOKEN")}'
                }, data={
                    "name": "main",
                    "developers_can_push": "true",
                    "developers_can_merge": "true"
                })
                print(protected_branch.json())

                # **** DEPRECATED: ****
                #protected_branch = requests.patch(f'https://{os.getenv("GITLAB_HOST")}/api/v4/projects/courses%2Fdit345%2F2023%2Fgroups%2Fa4-group-{grp_num}/protected_branches/main', headers={
                #    "PRIVATE-TOKEN": f'{os.getenv("PERSONAL_ACCESS_TOKEN")}',
                #    "Content-Type": "application/json"
                #}, data={
                #    "merge_access_levels": '[{"access_level": 30}]',
                #    "push_access_levels": '[{"access_level": 30}]'
                #})
                #print(protected_branch.json())

                ## Do api call and make new pipeline trigger token for the current test repo made
                create_triggertoken = requests.post(f'https://{os.getenv("GITLAB_HOST")}/api/v4/projects/courses%2Fdit345%2F2023%2Ftests%2Fa4-group-{grp_num}-test/triggers', headers={"PRIVATE-TOKEN": f'{os.getenv("PERSONAL_ACCESS_TOKEN")}'}, data={
                    "description": f'group-{grp_num}'
                }).json()
                print("Trigger token? ", create_triggertoken)

                ## Move it there, and add that to the CI variable of the GROUP repo
                ci_cd = requests.post(f'https://{os.getenv("GITLAB_HOST")}/api/v4/projects/courses%2Fdit345%2F2023%2Fgroups%2Fa4-group-{grp_num}/variables', headers={"PRIVATE-TOKEN": f'{os.getenv("PERSONAL_ACCESS_TOKEN")}'},
                        data={
                            "key": "YOUR_TOKEN",
                            "value": f'{create_triggertoken.get("token")}'
                        })
                
                ci_cd_test = requests.post(f'https://{os.getenv("GITLAB_HOST")}/api/v4/projects/courses%2Fdit345%2F2023%2Ftests%2Fa4-group-{grp_num}-test/variables', headers={"PRIVATE-TOKEN": f'{os.getenv("PERSONAL_ACCESS_TOKEN")}'}, data={
                    "key": "TEST_TOKEN",
                    "value": f'{os.getenv("GROUP_TOKEN")}'
                })

                print("Token added to group repo?", ci_cd.json())
                print("Token added to test repo?", ci_cd_test.json())

                # Looping through all of the members in the prev list, and doing a request to add them to the group number specified in the group's answer.
                for member in members:

                    # Using Gitlab's API, it is possible to send to it an HTTP post request, to the endpoint below, specifying which members to add in the flags of the URL.
                    # For every member, it will add the Gitlab acc assigned to that ID to the group which was specified in the answer. 
                    add = requests.post(f'https://{os.getenv("GITLAB_HOST")}/api/v4/projects/courses%2Fdit345%2F2023%2Fgroups%2Fa4-group-{grp_num}/members/?user_id={int(member.strip())}&access_level=30', headers={"PRIVATE-TOKEN": f'{os.getenv("PERSONAL_ACCESS_TOKEN")}'})
                    add_test = requests.post(f'https://{os.getenv("GITLAB_HOST")}/api/v4/projects/courses%2Fdit345%2F2023%2Ftests%2Fa4-group-{grp_num}-test/members/?user_id={int(member.strip())}&access_level=20', headers={"PRIVATE-TOKEN": f'{os.getenv("PERSONAL_ACCESS_TOKEN")}'})

                    # Check output from executed HTTP request (whether the person was added in his/her group's repo or not)
                    print("Added in group repo? ", add.json())
                    print("Added in test repo? ", add_test.json())

                    # Privileges: Group repo: Developer, Test repo: Reporter

            else:
                print("No group members invited for group " + grp_num + ". It may be that the repo already exists, or repo initialization failed.")
        
        # Useful set of commands to set "Shared Runners" enabled to be run, when groups and test repos are initialized.
        # Courtesy: https://gitlab.com/gitlab-org/gitlab/-/issues/29161

        gl = gitlab.Gitlab(url=f'https://{os.getenv("GITLAB_HOST")}', private_token=f'{os.getenv("PERSONAL_ACCESS_TOKEN")}')
        group = gl.groups.get("courses/dit345/2023/tests")
        projects = group.projects.list(archived=0, all=True)
        
        group_ = gl.groups.get("courses/dit345/2023/groups")
        a_projects = group_.projects.list(archived=0, all=True)
        
        for project in projects:
            pt = gl.projects.get(project.id)
            pt.shared_runners_enabled = True
            pt.save()

        for a_project in a_projects:
            pt_ = gl.projects.get(a_project.id)
            pt_.shared_runners_enabled = True
            pt_.save()
        
        print("My program took", time.time() - start_time, "to run..")

except ValueError as v:
    traceback.print_exc()
    print("For group " + grp_num + ", User IDs are not provided correctly, or the group number is not correct.")
    print("My program took", time.time() - start_time, "to run")