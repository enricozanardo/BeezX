![Beez Blockchain Quality Gate](https://github.com/onezerobinary/BeezX/actions/workflows/beez_quality_gate.yml/badge.svg)

# BeezX

### How to trigger pytests
To trigger the tests you can use `make test-python` make target.

### How to trigger pylint
To trigger the linting of the codebase use `make lint-python` make target.


## Installation guide
The following installation guide is for Linux Ubuntu machines.

#### Install git
1. `sudo apt-get update`
2. `sudo apt-get upgrade`
3. `sudo apt-get install git`

#### Install Python 3.9
1. `sudo apt-get install python3.9`

#### Set Python 3.9 as default Python version
1. Navigate to `/usr/bin`
2. Run `ls -lrth /usr/bin/python*` and check if `/usr/bin/python3.9` is in the directory
3. Check for a Python symlink pointing to a specific Python version other than Python 3.9
4. Unlink python symlink using `sudo unlink python`
5. Link python using `sudo ln -s /usr/bin/python3.9 python`
6. Unlink python3 symlink using `sudo unlink python3`
7. Link python3 using `sudo ln -s /usr/bin/python3.9 python3`
8. Check default Python versions via `python --version`and `python3 --version`. Both should show the same Python version Python 3.9.x

#### Install Curl
`sudo apt-get install curl`

#### Install Pip
`sudo apt-get install python3-pip`

#### Clone BeezX repository
1. Move to the directory you want to repository to be placed in (f.e. ~)
2. Run `git clone https://github.com/onezerobinary/BeezX.git`

#### Install BeezX requirements
1. Move to BeezX
2. Run `pip install -r requirements/requirements.txt`
3. Run `pip install -r requirements/requirements.in`

#### Set environment variables
1. Open `~/.bashrc`
2. Add `export BEEZ_NODE_KEY_PATH=path/to/privatekey.pem`
3. Add `export NODE_API_PORT=80`
4. Add `export FIRST_SERVER_IP=213.171.185.198`
5. Add `export P_2_P_PORT=5444`
6. Relead bash by running `source ~/.bashrc`

#### Start BeezX Node in background
1. Navigate to `BeezX`
2. Run `nohup python main.py &`
3. Check if Node is running via `curl yourip:5445/info` you should see an output similar to `This is Beez Blockchain!. 🦾 🐝 🐝 🐝 🦾





