# Canvas - Gitlab Group-Assigner - written in Python
1. Clone this repo, and additionally, clone the `a4-group-xx` and `a4-group-xx-test` folders in this directory.
2. Download the Survey results from canvas as a `.csv` file, and preferably should be named by default, when downloaded, `'Survey Group Registration Survey Student Analysis Report.csv'`. Add that to this folder.
3. Initialise also a `.env` file, that stores the necessary tokens for initializing the repos, and to be able to use that to communicate with the Gitlab API to do further actions like inviting new members, moving repo to a Gitlab Group, modifying repo settings etc, all **taken care of** in this script itself.
```
group-assigner/
├─ group-assigner.py
├─ a4-group-xx-test/
├─ a4-group-xx/
├─ Survey Group Registration Survey Student Analysis Report.csv
├─ .env
```
**Note:** Make sure to have the group-xx templates cloned via SSH, so that the script can batch-make the repos efficiently, and one does not need to enter login creds during every initialization step.

3. Run the script:
 ```
 $ python3 group-assigner.py
 ```
4. If any errors occur s.a. libraries are not found, then simply install them using `pip install ..`.
5. When the script is finished, based on **1) the group numbers from the student answers**, and **2) the Gitlab User IDs** that students were meant to provide, the project groups will be made on Gitlab, and the right users matching the IDs will be added, with role of **Developer** in the group repository, and **Reporter** in the test repository. One group repo and one test repo is made, per team.
6. On the local machine where this automation script was run, all of the made repos will be locally stored under a file called `assignment-grps`. One can simply delete that, in order to remove the collection of **local copies** of the batch-generated repos, if one wishes to.

> DIT345 - Aditya Khadkikar
