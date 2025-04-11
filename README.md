# Project Documentation

# Web News Portal Application

The practical task involves developing and containerizing a Django-based news application that supports role-based content management and newsletter/article publishing. The project allows journalists to create and submit newsletters and articles, while editors can approve, edit, or delete content directly within the application rather than through Django’s admin interface.

**Frameworks and Technologies:**

- **Django (with Django REST Framework):** Used for building the web application, handling user authentication (including a custom user model), and rendering templates for dynamic content.
- **MariaDB:** Serves as the application's database, configured to run on port 3307.
- **Docker:** Containerizes the Django project, ensuring consistent deployment across different environments. Gunicorn is used as the application server for production readiness.

**Usage Examples:**

- **Articles Display:** The application fetches and orders articles by creation date; the newest article is featured prominently, while subsequent articles are arranged in a grid layout.
- **User Operations:** Journalists can submit newsletters or articles, and editors have the ability to manage (approve/reject/edit) content via in-application workflows.
- **Containerization:** Dockerfile and docker-compose configurations have been created to package the application and its dependencies, allowing the app to run in an isolated container.

**Configuration Details:**

- **DATABASES Setting:** Updated to use host.docker.internal as the HOST within the container to connect to the host’s MariaDB instance.
- **Dockerfile:** Installs necessary system dependencies, sets up the Python environment, and uses Gunicorn for serving the application.
- **Environment Variables:** Configured in the Dockerfile (e.g., PYTHONDONTWRITEBYTECODE, PYTHONUNBUFFERED) to improve runtime performance.

**Prerequisites:**

- Intermediate knowledge of Django and Python.
- Familiarity with Docker and containerization concepts.
- Basic understanding of relational databases (MariaDB/MySQL) and web server configuration.

This summary encapsulates the objectives, frameworks, and configurations implemented in the project thus far. This application, built with Django, showcases CRUD capabilities, a responsive design through Bootstrap, and a modular project structure. It employs unit testing following the AAA pattern. Every template incorporates semantic HTML elements (header, section, article, footer) and Bootstrap classes to achieve a responsive and polished design.

Organised project structure extends to the Web News Application with a secure RESTful API and also integrates Twitter’s API to tweet when news articles are posted and published. This Django-based News Web Application allows readers to view articles and newsletters published by independent journalists and publishers. It includes role-based authentication, article approval workflows (with email and X (formerly Twitter) notifications), and a RESTful API for third-party access.

## TESTING

- Testing with Console Email Backend:
  For development purposes, you might want to use the console email backend
  (which prints emails to the console) to bypass SMTP credentials issue.
  This can be found in settings.py.

## READER | JOURNALIST | EDITOR INFORMATION

| Reader01      |                   |
| ------------- | ----------------- |
| **username:** | JohnDoe           |
| **email:**    | DoeJohn@email.com |
| **password:** | P@55w0Rd4528_DJ   |

| **Reader02**  |                    |
| ------------- | ------------------ |
| **username:** | JaneDoe            |
| **email:**    | DoeJane@email.com  |
| **password:** | P@55w0Rd4528_MrsDJ |

| Reader03      |                     |
| ------------- | ------------------- |
| **username:** | PlainJane           |
| **email:**    | JanePlain@email.com |
| **password:** | P@55w0Rd4528_MrsPJ  |

| Journalist01  |                     |
| ------------- | ------------------- |
| **username:** | JohnApple           |
| **email:**    | AppleJohn@email.com |
| **password:** | P@66w0Rd4528_DJ     |

| Journalist02  |                      |
| ------------- | -------------------- |
| **username:** | JohnBanana           |
| **email:**    | BananaJohn@email.com |
| **password:** | P@66w0Rd4528_BJ      |

| Journalist03  |                      |
| ------------- | -------------------- |
| **username:** | PeterSmith           |
| **email:**    | SmithPeter@email.com |
| **password:** | P@66w0Rd8628_PS      |

| Journalist04  |                     |
| ------------- | ------------------- |
| **username:** | JohnSmith           |
| **email:**    | SmithJohn@email.com |
| **password:** | P@36w0Rd8918_JS     |

| Editor01      |                      |
| ------------- | -------------------- |
| **username:** | BigMac               |
| **email:**    | MacBigMeal@email.com |
| **password:** | P@66w0Rd4528_BMM     |

## 1. Project Structure

    django_project_news/                        # Project folder dir
    │
    ├── myVenv
    │
    └── news_project/                           # Proj. ROOT folder dir. (UPPER / OUTER) proj. dir.
       │
       ├── __init__.py
       ├── .dockerignore
       ├── Dockerfile
       ├── manage.py                            # Django management script
       ├── README.md                            # Django project description
       ├── .flake8
       ├── .pyproject.toml
       ├── requirements.txt                     # Project dependencies
       ├── .gitignore
       ├── db.sqlite3                           # (For development. → Will switch to MariaDB)
       │
       |
       ├── docs/
       |
       ├── news_project/                        # Main (CORE / INNER) proj. folder (Contains proj. settings)
       │  ├── __init__.py
       │  ├── settings.py                       # Glob. config. settings (incl. installed apps, static files, etc.)
       │  ├── urls.py                           # Main / Root URL dispatcher. Defines the main URL routes
       │  ├── wsgi.py
       │  └── asgi.py
       │
       │
       │ ==== # Folders for Django apps START here # ====
       │
       ├── newsApp/                             # Our news website application called 'newsApp'
       │  ├── migrations/
       │  │  └── __init__.py
       │  ├── __init__.py
       │  ├── admin.py                          # Model reg. for Django admin
       │  ├── apps.py                           # App configuration
       │  ├── models.py                         # Core data Models: CustomUser, Publisher, Article, and Newsletter etc.
       │  ├── forms.py                          # Forms for user reg., article submission, etc.
       │  ├── views.py                          # Views (Contains view functions for user registration, login, logout, dashboard, article creation, etc.)
       │  ├── urls.py                           # App-specific URL patterns for web views.
       │  ├── tests.py                          # Unit tests for models and views following AAA pattern.
       │  ├── static/
       │  │  └── newsApp/
       │  │     ├── css/
       │  │     │  └── styles.css               # Custom CSS (with Bootstrap added via CDN in templates)
       │  │     └── js/
       │  │        └── scripts.js               # (Optional) Custom JavaScript
       │  │
       │  ├── serializers.py                    # Creating Serializers. Model sterilisation. Creates serializers to convert Django model instances to JSON for API interaction.
       │  │
       │  ├── signals.py                        # Sends automated emails to subscr. and is responsible for posting articles to X upon approval.
       │  │
       │  ├── api_views.py                      # Building API Views. Creates API endpoints for
       │  │ data retrieval. Defines RESTful API views.
       │  │
       │  ├── api_urls.py                       # Setting Up API URLs. Endpoint registration. API endpoint mapping.
       │  │
       │  │
       │  ├── functions/
       │  │  └── tweet.py                       # Integrating Twitter API—tweets are sent using this class.
       │  │  └── __init__.py
       │  │
       │  │
       │  └── templates/
       │    └── newsApp/
       │       ├── base.html                    # Base template with Bootstrap & semantic HTML
       │       ├── register.html                # User registration form
       │       ├── login.html                   # User Login form
       │       ├── dashboard.html               # Dashboard showing options based on user role.
       │       ├── article_form.html            # Create/edit; Form for journalists to create a new article.
       │       ├── article_approval.html        # Lists pending articles for editors approval.
       │       ├── article_list.html            # Lists all approved articles for public viewing.
       │       ├── article_detail.html          # Displays details of a completed article.
       │       ├── article_edit.html            # Edits details of an article.
       │       ├── article_confirm_delete.html  # Displays delete confirm message of an article.
       │       ├── article_confirm_update.html  # Displays update confirm message of an article.
       │       ├── article_edit_form.html       # Edit details of an article.
       │       ├── subscriptions.html           # Displays readers subscriptions page.
       │       ├── newsletter_list.html         # Displays newsletters.
       │       ├── newsletter_detail.html       # Displays newsletters details.
       │       ├── newsletter_create.html       # Newsletters creation file.
       │       ├── newsletter_edit.html         # Newsletters editing file.
       │       ├── newsletter_delete.html       # Newsletters deletion file.
       │       ├── all_newsletters.html         # displays all newsletters.
       │       ├── pending_newsletters.html     # structure you can use if you decide to create a dedicated template newsletters.
       │       └── journalist_articles.html     # Displays readers journalists' subscriptions page.
       │
       │ ==== # Folders for Django apps END here # ====
       │
       │
       │
       ├── templates/                           # Global templates folder
       │  ├── base.html # Base HTML template
       │  └── ...
       │
       └── static/                              # (Optional) Glob. static files (e.g., CSS, JavaScript, images)
          ├── css/
          ├── js/
          └── images/

    OPTIONAL:
    For .flake8:
    [flake8]
    max-line-length = 79
    exclude = .git,__pycache__,tests,venv
    ignore = E203, E266, W503

    OPTIONAL:
    For .pyproject.toml:tg
    [tool.black]
    line-length = 79

## 2. Setup Instructions

1.  **Create 'django_project_news' folder in file explorer.**

        "C:\...\django_project_news" => project folder dir

2.  **Create a virtual environment - while in project folder dir**

         Type: 'python -m venv myVenv' into vs code terminal

    2.1. **Activate virtual environment**

         Type: 'source myVenv/Scripts/activate' into vs code terminal, then
         Type: 'pip freeze' into the vs code term.

3.  **Install django - still while in project folder dir**

        Type: 'pip install django' into the vs code terminal, then
        Type: 'pip freeze' into the vs code term.

4.  **Create a new django project and application**

    4.1. **Create a new django project:**

        Type: 'django-admin startproject news_project' into vs code term, while still in proj. folder dir

    4.2. **Change directory to proj ROOT dir**

        Type: 'cd news_project' into vs code term

    4.3. **Create a new Django application:**

        Type: 'django-admin startapp newsApp' into vs code term
        Type: 'ls' into vs code term

5.  **Run initial database migrations to set up the database tables:**

        Type: 'python manage.py migrate' into the vs code term

6.  **Create a superuser to access the Django admin interface:**

        Type: 'python manage.py createsuperuser' into the vs code term, then,
        Fill in: username (James --this is a fictitious username), email (rrrr@rrrr.com), password (1234 --this is a fictitious password)

7.  **Start the Django development server:**

        Type: 'python manage.py runserver' into the vs code term, then follow the http://... link in term

8.  **Create the necessary subfolders and modules where needed within the proj folder dir or proj root dir**

9.  **Edit and populate the different modules and subfolders**

10. **Install flake8:**

        Type: 'pip install flake8' into the vs code term and create and populate the .flake8 file.

11. **Install Black:**

        Type: 'pip install black' into the vs code term

12. **Perform black and flake8 PEP 8 standards. >>> Use prettier with caution on HTML, CSS, JavaScript. It causes app errors**

13. **Install MySQL on your local machine, define host, port, username, and password accordingly.**

        Then, connect to your MySQL server.

14. **Run Migrations:**

        Open your terminal and execute the following commands in your project’s ROOT directory:
        Type: 'python manage.py makemigrations'
        'python manage.py migrate' into the vs code term

15. **Restart Your Development Server:**

        Type: 'python manage.py runserver' into the vs code term, then follow the http://... link in term

16. **Use your application and check if it works.**
17. **Generate requirements.exe file:**

        Type: 'pip freeze > requirements.txt' into vs code term, while in proj root dir.

    17.1. **Always keep the requirements.txt file updated to include all necessary dependencies.**

18. **Generate README.md file.**

        NOTE: Perform migrations to ensure that any new changes are reflected in the database, and restart the development server to test your application.

    **NOTE:** ALWAYS CHECK THAT YOUR README.md FILE CONTENTS / CHARACTERS ARE DISPLAYED CORRECTLY BEFORE FINAL DEPLOYMENT OF APPLICATION! → The application of flack8 and black can cause display errors.

19. **Install djangorestframework:**

        Type: 'pip install djangorestframework' into the vs code term, while still in the proj root dir.

20. **Install requests:**

        Type: 'pip install requests' into the vs code term, while still in the proj root dir.

21. **Install mysqlclient:**

        Type: 'pip install mysqlclient' into the vs code term, while still in the proj root dir.

22. **Run Migrations:**

        Open your terminal and execute the following commands in your project’s ROOT directory:
        Type: 'python manage.py makemigrations'
        'python manage.py migrate' into the vs code term

23. **Perform application functionality tests:**

### FUNCTIONALITY TESTING:

24. **Manual (Functional) Testing:**

    1.  Basic Project Setup

        1.1. Activate your virtual environment and install dependencies:

            pip install -r requirements.txt

        1.2. Apply migrations and create a superuser:

            python manage.py makemigrations
            python manage.py migrate
            python manage.py createsuperuser

        1.3. Run the server:

            python manage.py runserver

        1.4. Access the application in your browser at

            http://127.0.0.1:8000/

    2.  Testing the Admin Site

            Go to http://127.0.0.1:8000/admin/ → Log in using your superuser credentials → Create or view data (e.g., Publishers, Articles, CustomUser, etc.) → Verify that you can add/edit/delete records via the admin interface.

    3.  Testing Registration & Login
    4.  Testing Role-Based Access
    5.  Testing via Postman

25. **Install Postman:**

26. **Test GET Endpoints:**

- Test the endpoint that lists all articles, set the method to **GET** within Postman.
  Use the URL: 'http://127.0.0.1:8000/api/articles/' and click send.
  use basic auth → a readers credentials then a journalist credentials.

  26.1. **Inspect the JSON response in Postman**

  - You should receive **200 OK** message.

26. **Test POST Endpoints:**

- Test the endpoint that creates a new article, set the method to **POST** in Postman.

  use the URL: 'http://127.0.0.1:8000/api/articles/', then in the Authorization tab, choose Basic Auth and enter one of your journalists username and password.

  - In the Body tab, select raw and choose JSON as the type.

  Type:

  ```json
  {
    "title": "My New Article",
    "content": "This is the body of my article.",
    "status": "pending"
  }
  ```

  into the field → then click send

  - If successful, you should receive a JSON response with the new article’s data and an HTTP status code of **201**.

27. **Run tests once again. i.e.**

        Type: 'python manage.py test' and 'python manage.py test --verbosity 2' into the vs code term.

## 3. Frequently used commands

    django-admin startproject news_project

    django-admin startapp newsApp

    python manage.py migrate

    python manage.py createsuperuser

    python manage.py runserver

    python manage.py makemigrations
    python manage.py migrate

    python manage.py makemigrations && python manage.py migrate

    http://127.0.0.1:8000/admin/

    pip freeze > requirements.txt

This command recursively searches your project directory for any folders named pycache and deletes them.

    find . -type d -name "__pycache__" -exec rm -rf {} +

### 3.1. Frequently used _Test Commands_

    python manage.py test

    python manage.py test --verbosity 2

## 4. Appendix

### 4.1. Workflow Procedure

1.  **Set up your local repository:**

    1.1. Create a public repository on GitHub called my_news_application

    1.2. Upload all the relevant project application files to the repository which you have created on GitHub.

    1.3. Clone the my_news_application repository to your local machine in a directory of choice—using the git clone command within the Windows command prompt terminal:

        git clone https://github.com/weberjarred/my_news_application.git

    1.4. Navigate to the local repository folder:

        cd repository-folder

    1.5. Configure the remote link if it hasn't been set up yet, and verify that your local repository is linked to the GitHub repository by confirming the remote link. This command will create a remote link to the folder on your local machine:

        git remote -v

2.  **Create a local branch for the subsequent actions:**

    - Make a new branch to keep your changes separate. Begin by refreshing your local repository with updates from the main branch. Enter the following command in the terminal:
      git pull origin main

                              +---------------------------------------------------------------------------+
                              | now, work on the project in vs code... save and store changes locally as  |
                              | you work on the repository files that were cloned onto your local         |
                              | machine... keep your command prompt open...                               |
                              +---------------------------------------------------------------------------+
                                                      |
                                                      |
                                                     \|/
                                                      v


          - 2.1.1. Navigate to your project's root (UPPER) directory and install all packages and dependencies needed for the program to execute. Use the following command:

                  pip install -r requirements.txt

          - 2.1.2. Install MariaDB on your local machine and configure the DATABASES section in settings.py. An ENGINE, NAME (of your database), USER, PASSWORD (of the created database), HOST, PORT properties need to be assigned as needed, with respect to your database.

          - 2.1.3. Create an appropriate Dockerfile and .dockerignore file for your code—this will set the foundation for the Docker image which will be created.

          - 2.1.4. Build, run your Docker image and upload it to Docker Hub (installed locally) using the following command in the VS Code terminal:

                  docker build -t my-docker-news-image ./
                  docker images

          - 2.1.5. Create a Docker repository and rename your image to match your repository name. The format is [user]/[repo], where user is your Docker Hub username and repo is the repository’s name. Insert the following command:

                  docker tag my-docker-news-image [username]/[repository name]

          - 2.1.6. Upload your Docker image, using the command:

              Docker push [username]/[repository name]

          - 2.1.7. Run the Docker image and containerize and deploy the Django News Application with the following command in the VS Code terminal:

                  docker run -d --name my-docker-news-container -p [a]:[b] my-docker-news-image,
                  where;
                  a = your chosen port on which to run / map the docker image (e.g. 8001/2 etc..)
                  b = container port designation = 8000, in this case.

          - 2.1.8. Navigate to your docker desktop program installed to view your now active image and container. Clicking your designated port configuration chosen and on your local machine using the http://localhost domain.

**!!NOTE:** If you do wish to deploy your image and container on an alternate device or on Docker Playground, the host settings and allowed hosts should be correctly reconfigured. If allowed hosts are not configured, you will receive a disallowed hosts error.

                            +---------------------------------------------------------------------------+
                            | now, switch back to your still open command prompt window,..              |
                            +---------------------------------------------------------------------------+
                                        |
                                        |
                                       \|/
                                        v

3.  **Create a local branch and make the changes locally:**

    1.  Create a new branch named 'container', using the following command:

             git checkout -b feature/container

    2.  Once done, stage and commit the the changes. Use the following command:
        git add .

                 git commit -m "News Application Containerisation"

4.  **Push the branch to GitHub:**

    1.  After committing the changes, push the newly created branch to the remote repository. This will allow your changes implemented to be seen and available directly on GitHub. Use the following command to push the branchans changes to GitHub:

             git push origin feature/container

5.  **Open a pull request on GitHub—after pushing your branch.**

        → Once the 'Compare and pull request prompt' button appears, click this button.

6.  **Review pull request.**

7.  **Merge the pull request**

8.  **Close the latest / highlighted field—if not, the GitHub will automatically close the request made**

---

---
