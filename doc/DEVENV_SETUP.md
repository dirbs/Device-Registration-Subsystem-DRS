### Prerequisites
In order to run a development environment, [Python 3.0+](https://www.python.org/download/releases/3.0/) and 
[Postgresql10](https://www.postgresql.org/about/news/1786/) we assume that these are installed.

We also assume that this repo is cloned from Github onto the local computer, it is assumed that 
all commands mentioned in this guide are run from root directory of the project and inside
```virtual environment```

On Windows, we assume that a Bash like shell is available (i.e Bash under Cygwin), with GNU make installed.

### Starting a dev environment
The easiest and quickest way to get started is to use local-only environment (i.e everything runs locally, including
Postgresql Server). To setup the local environment, follow the section below:

#### Setting up local dev environment
For setting up a local dev environment we assume that the ```prerequisites``` are met already. To setup a local 
environment:
* Create database using Postgresql (Name and credentials should be same as in [config](mock/test-config.ini))
* Create virtual environment using **virtualenv** and activate it:
    ```bash
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
    Make sure that virtual-env is made using Python3 and all the required dependencies are installed.
* Run Database migrations using:
    ```bash
    make install-db
    ```
    This will automatically create and migrate database schemas and requirements.

* Start DRS development server using:
    ```bash
    make start-dev
    ```
    This will start a flask development environment for DRS.

* To run unit tests, run:
    ```bash
    make test
    ```

* To lint the code using pylint, simply run:
    ```bash
    make lint
    ```