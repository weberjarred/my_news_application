1. Set up your local repository:

1.1. Create a public repository on GitHub called my_news_application
1.2. Upload all the relevant project application files to the repository which you have created on GitHub.
1.3. Clone the my_news_application repository to your local machine in a directory of choice—using the git clone command within the Windows command prompt terminal:
	git clone https://github.com/weberjarred/my_news_application.git

1.4. Navigate to the local repository folder:
	cd repository-folder

1.5. Configure the remote link if it hasn't been set up yet, and verify that your local repository is linked to the GitHub repository by confirming the remote link. This command will create a remote link to the folder on your local machine:
	git remote -v


2. Create a local branch for the subsequent actions:
2.1. Make a new branch to keep your changes separate. Begin by refreshing your local repository with updates from the main branch. Enter the following command in the terminal:
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
2.1.1. Navigate to your project's root (UPPER) directory and install all packages and dependencies needed for the program to execute. Use the following command:
	pip install -r requirements.txt

2.1.2. Install MariaDB on your local machine and configure the DATABASES section in settings.py. An ENGINE, NAME (of your database), USER, PASSWORD (of the created database), HOST, PORT properties need to be assigned as needed, with respect to your database.
2.1.3. Create an appropriate Dockerfile and .dockerignore file for your code—this will set the foundation for the Docker image which will be created.
2.1.4. Build, run your Docker image and upload it to Docker Hub (installed locally) using the following command in the VS Code terminal:
	docker build -t my-docker-news-image ./
	docker images

2.1.5. Create a Docker repository and rename your image to match your repository name. The format is [user]/[repo], where user is your Docker Hub username and repo is the repository’s name. Insert the following command:
	docker tag my-docker-news-image [username]/[repository name]

2.1.6. Upload your Docker image, using the command:
	Docker push [username]/[repository name]
2.1.7. Run the Docker image and containerize and deploy the Django News Application with the following command in the VS Code terminal:
	docker run -d --name my-docker-news-container -p [a]:[b] my-docker-news-image, 
	where;
	a = your chosen port on which to run / map the docker image (e.g. 8001/2 etc..)
	b = container port designation = 8000, in this case.

2.1.8. Navigate to your docker desktop program installed to view your now active image and container. Clicking your designated port configuration chosen and on your local machine using the http://localhost domain.

!!NOTE: If you do wish to deploy your image and container on an alternate device or on Docker Playground, the host settings and allowed hosts should be correctly reconfigured. If allowed hosts are not configured, you will receive a disallowed hosts error.



+---------------------------------------------------------------------------+
| now, switch back to your still open command prompt window,..              |                    |                                                                           |
+---------------------------------------------------------------------------+
                         |
                         |
                        \|/
                         v


3. Create a local branch and make the changes locally:
3.1. Create a new branch named 'container', using the following command:
	git checkout -b feature/container
3.2. Once done, stage and commit the the changes. Use the following command:
	git add .
	git commit -m "News Application Containerisation"
4. Push the branch to GitHub:
4.1. After committing the changes, push the newly created branch to the remote repository. This will allow your changes implemented to be seen and available directly on GitHub. Use the following command to push the branchans changes to GitHub:
	git push origin feature/container
5. Open a pull request on GitHub—after pushing your branch.
	→ Once the 'Compare and pull request prompt' button appears, click this button.
6. Review pull request.
7. Merge the pull request
8. Close the latest / highlighted field—if not, the GitHub will automatically close the request made

































