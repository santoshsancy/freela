# README #
# Getting set up #


### Step 0: Create an SSH Key for your bitbucket account ###

ssh-keygen -t rsa -b 4096 -C "youremail@example.com"

eval "$(ssh-agent -s)"

ssh-add ~/.ssh/id_rsa

Add your public key to your bitbucket account

### Step 1: clone the repository: (substitute your username) ###

git clone git@bitbucket.org:umichdig/healthyminds.git

###Step 2: create a virtualenv to run your code:###

brew install python3

pip install --upgrade virtualenv

virtualenv -p python3 env

### Step 3: Activate the environment: ###

source env/bin/activate

### Step 4: Install the required packages:###

pip install -r requirements.txt

###Step 5: create a database for the project###

Example:
shell> mysql --user=root mysql

**If you've assigned a password to the root account, you'll also need to supply a --password option.**

mysql> CREATE DATABASE local_shift

mysql> CREATE USER 'local_shift'@'localhost' IDENTIFIED BY 'obscure';

mysql> GRANT ALL PRIVILEGES ON local_shift.* TO 'local_shift'@'localhost';

###Step 6: Create a local.py file in the settings folder###
** You can use the provided example to start**

cp settings/local_example.py settings/local.py

**Inside local.py update the database name, user, password to reflect the ones you've created**

**Also be sure to update your DJANGO_SETTINGS_MODULE setting **
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.local'

###Step 7: Run the database migrations###

python manage.py migrate

###Step 8: Install LESS and YUGLIFY for pipelined CSS PreProcessing ###

sudo npm -g install less

sudo npm -g install yuglify

###Step 9: Run your localhost###

python manage.py runserver
