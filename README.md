* Project license has been updated to remove the requirement for acknowledgement
---

![Image of DIRBS Logo](https://avatars0.githubusercontent.com/u/42587891?s=100&v=4)

# Device Registration Subsystem API
## License
Copyright (c) 2018-2021 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
* The origin of this software must not be misrepresented; you must not claim that you wrote the original software.
* Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
* This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


## Documentation
[DRS-API-Installation-Guide-1.0.0](https://github.com/dirbs/Documentation/blob/master/Device-Registration-Subsystem/DRS-API-Installation-Guide-2.0.0.pdf)

[DRS-SPA-Installation-Guide-1.0.0.pdf](https://github.com/dirbs/Documentation/blob/master/Device-Registration-Subsystem/DRS-SPA-Installation-Guide-1.0.0.pdf)

[DRS-Importer-User-Guide-1.0.0.pdf](https://github.com/dirbs/Documentation/blob/master/Device-Registration-Subsystem/DRS-Importer-User-Guide-1.0.0.pdf)

[DRS-Exporter-User-Guide-1.0.0.pdf](https://github.com/dirbs/Documentation/blob/master/Device-Registration-Subsystem/DRS-Exporter-User-Guide-1.0.0.pdf)

[DRS-Authority-User-Guide-1.0.0.pdf](https://github.com/dirbs/Documentation/blob/master/Device-Registration-Subsystem/DRS-Authority-User-Guide-1.0.0.pdf)

## Frontend Application Repo
https://github.com/dirbs/Device-Registration-Subsystem-Frontend

## Directory structure
This repository contains code for **DRS** part of the **DIRBS**. It contains
* ``app/`` -- The DRS core server app, to be used as DRS Web Server including database models, apis and resources
* ``etc/`` -- Config files etc to be reside here
* ``mock/`` -- Sample data files etc which are used in app to be reside here
* ``scripts/`` -- Database migration, list generation scripts etc
* ``tests/`` -- Unit test scripts and Data

---


## Starting Dev Environment
_Make sure you have installed [docker](https://docs.docker.com/install/) and 
[docker-compose](https://docs.docker.com/compose/install/).
To install dev environment without docker follow [here](doc/DEVENV_SETUP.md)._
- Clone the repository
- Create a `drs` user with UID `9001` and change the ownership of the repo:
    ```bash
    sudo useradd -u 9001 -m -d /home/drs -s /bin/bash drs
    sudo chown -R 9001:9001 Device-Registration-Subsystem
    ```
- Now build Dev Server using:
    ```bash
    make -f docker/dev/Makefile
    ```
- Build Postgres Server using:
    ```bash
    make -f docker/postgres/Makefile
    ```
- After the build process for both images is successful launch dev environment using docker-compose:
    ```bash
    docker-compose -f docker/dev/devenv-with-local-db.yml run --rm --service-ports dev-shell
    ```
    It will launch container for development server and for postgres (drs_db) and login you to the shell
    of the development server.

- Now open another terminal and login into the postgres shell:
    ```bash
    docker exec -it drs_db bash
    ```

- Checkout into the postgres shell:
    ```bash
    gosu postgres psql
    ```

- On the postgres shell, create a role `drs` with login:
    ```bash
    CREATE ROLE drs WITH login;
    ```

- On the postgres shell, create database named `drs`:
    ```bash
    CREATE database drs OWNER drs;
    ```

- Now switch to the server shell, and install database:
    ```bash
    make install-db
    ```

    After these steps are completed successfully, you can run test or start development server etc on the shell.

---


### Bumping version number
We follow [Semantic Versioning](http://semver.org/) for DRS.
To change the releases number simply edit ```app/metadata.py``` and bump the version number.

---

### Other Helpful Commands

To clean the extra and un-necessary directories in the project:
```bash
make clean
```

To clean the python compiled files from the project:
```bash
make clean-pyc
```

To install a fresh database:
```bash
make install-db
```

To Upgrade already installed database:
```bash
make upgrade-db
```
To configure
To create distribution files:
```bash
make dist
```

To generate full registration list for DIRBS Core:
```bash
make genlist-full
```

To generate delta registration list for DIRBS Core:
```bash
make genlist-delta
```

To run unit and regression tests:
```bash
make test
```

To run code linting:
```bash
make lint
```

To generate languages:
```bash
pybabel extract -F babel.cfg -k _l -o messages.pot .
pybabel init -i messages.pot -d app/translations -l language-code
pybabel compile -d app/translations
```

Install rabbitmq-server
```bash
$ sudo apt-get install rabbitmq-server
```

Start celery worker
```bash
$ celery -A app.celery worker --loglevel=info -B
```
