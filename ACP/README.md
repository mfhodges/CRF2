

code to support any process for emergency closure.

All of the processes written here will be run from the command line on the server.


Before running any of these scripts please pull in the instructors and courses for the given term. This can be run with UI from `/admin/django_celery_beat/periodictask/` 


## Steps
- Make sure that the SRS data in the CRF is up to date.
    - run `task_pull_courses(term)` in `course/tasks.py` ( this can also be done in the UI from `/admin/django_celery_beat/periodictask/` )
    - run `task_pull_instructors(term)` in `course/tasks.py` ( this can also be done in the UI from `/admin/django_celery_beat/periodictask/` )
- ssh onto the CRF server, navigate to the app and start the venv. 
- in `crf2/` ( *not* `crf2/crf2/` ) and start a django shell: `$ python3 manage.py shell`
- import the following
```
>>> from ACP.canvas_sites import *
>>> from ACP.create_course_list import *
```
- run `>>> create_unrequested_list(outputfile='notRequestestedSIS.txt',term)` where term is the academice term (e.g. '2020A')

## Default Files 
There are some default arguments for file names that are recommended for clarity. There are also log files which document most errors that the scripts may encounter. 

### `data/`
- 'notRequestestedSIS.txt' - a list of course codes for primary courses that exist in the CRF and have not been requested yet (footnote: this is limited to the visible schools)
- 'notUsedSIS.txt' - the above file cross referenced ( word choice?) with SIS IDs currently in use in Canvas. 
- 'requestProcessNotes.txt' - (**name cannot be changed**) notes about errors or information ( reword ). this includes new Canvas accounts that have been created, failure to add a user, failure to properly set up the site.
- 'canvasSitesFile.txt' - (**name cannot be changed**) a like of course codes and canvas site ids of sites that have been made in this provisioning process

### `logs/`
- canvas.log - documents errors that have occured when processing a Request or when configuring a site. 
- crf.log - documents errors that have occured in the CRF such as failure to find/create a Request.
- email.log - documents erros that have occured when notifying instructors that a canvas site has been created for their course. 

## Sunsetting
TBA

## Areas for improvement
- **Emailing needs to be set up.**

- Currently the form creates each course as a single section site. With some effort some of these sites could be set up as multi section sites if some inferencing based on intructors and tas was developed.

- Have this fully managed by the UI so there is no programming limitation.