
**🛠 DRAFT 📝**

Code to support any process for emergency closure.
All of the processes written here will be run from the command line on the server.


## Steps
After step 5 the script will prompt the user with the next step.

1. Make sure that the SRS data in the CRF is up to date.
    - run `task_pull_courses(term)` in `course/tasks.py` ( this can also be done in the UI from `/admin/django_celery_beat/periodictask/` )
    - run `task_pull_instructors(term)` in `course/tasks.py` ( this can also be done in the UI from `/admin/django_celery_beat/periodictask/` )
2. ssh onto the CRF server, navigate to the app and start the venv. 
3. in `crf2/` ( *not* `crf2/crf2/` ) start a django shell: `$ python3 manage.py shell`
4. import the following
    ```
    >>> from ACP.canvas_sites import *
    >>> from ACP.create_course_list import *
    ```
5. run `>>> create_unrequested_list(outputfile='notRequestestedSIS.txt',term)` where `term` is the academic term (e.g. '2020A')
6. run `>>> create_unused_sis_list(inputfile='notRequestestedSIS.txt',outputfile='notUsedSIS.txt')` to create a list of SIS IDs not in use in canvas
7. run `>>> create_requests(inputfile='notUsedSIS.txt',copy_site='')`
8. run `>>> process_requests(file='notUsedSIS.txt')`
9. (OPTIONAL) run `config_sites()` with the desired parameters to configure all sites. see code/function for information on parameters'

## Default Files 
There are some default arguments for file names that are recommended for clarity. There are also log files which document most errors that the scripts may encounter. 

### `data/`
- 'notRequestestedSIS.txt' - a list of course codes for primary courses that exist in the CRF and have not been requested yet (note: this is limited to the visible schools in the CRF)
- 'notUsedSIS.txt' - removes course codes with SIS IDs currently in use in Canvas from the above file. 
- 'requestProcessNotes.txt' - (**name cannot be changed**) list notes about errors or process notes that occurred when creating a Canvas site for each Request. This includes new Canvas accounts that have been created, failure to add a user, failure to properly set up the site.
- 'canvasSitesFile.txt' - (**name cannot be changed**) a list of course codes and canvas site ids of sites that have been made in this provisioning process.

### `logs/`
- canvas.log - documents errors that have occurred when processing a Request or when configuring a site. 
- crf.log - documents errors that have occurred in the CRF such as failure to find/create a Request.
- email.log - documents errors that have occurred when notifying instructors that a canvas site has been created for their course. 

## Configuring sites
The following configurations are possible: 
These can all be run sequentially with the `config_sites()` function or run independently.
- Pre-populate with Resources: `copy_content(inputfile,source_site)`
- Increase Storage Quota: `inc_storage(inputfile,capacity=2)`
- Enable LTIs: automatically configure Panopto. `enable_lti(inputfile,tool)`
- Publish the site: `publish_sites(inputfile)`

## Sunsetting
TBA
1. Reduce Storage Quota (where applicable)
2.  

## Areas for improvement
- **Emailing needs to be set up.**

- Currently the CRF creates each course as a single section Canvas site. With some effort, some of these sites could be set up as multi-section sites if some inferences based on instructors and TAs was developed.

- Have this fully managed by the UI so there is no programming limitation.

--- 
Madeleine Hodges, 2020