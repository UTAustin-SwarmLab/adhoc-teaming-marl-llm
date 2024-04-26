# Project Setup Instructions
## DockerFile
Dockerfile provided in adhoc-teaming/docker

## Build a docker image and container 

#### Sample commands provided for MACOS as follows:
   ```
   cd adhoc-teaming/docker
   docker image build --platform linux/amd64 -t  marl-teaming .
   docker container create -it --name teaming -p 8081:8081 -v /Users/hg22723/Phd/Research/P2-AdHocTeaming/adhoc-teaming-marl-llm:/code/ marl-teaming:ubuntu20.04-cuda11.3
   ```

  Change the mount volume (-v) to the path of the project: [Yourfolder]:/code

#### Sample commands provided for Linux as follows:

   ```
   cd adhoc-teaming/docker
   docker image build -t marl-teaming .
   docker container create -it --name teaming -p 8081:8081 -v /Users/hg22723/Phd/Research/P2-AdHocTeaming/adhoc-teaming-marl-llm:/code/ marl-teaming:ubuntu20.04-cuda11.3
   ```

Set the --gpus tag if you want to use GPUs.

## Running experiments and development

Enter your docker container and set up marllib.
   ```
  docker attach teaming
  cd /code/adhoc-teaming/
  pip install marllib/requirements.txt
   ```

##### 1. Running experiments on original LBF environment
   ```
PYTHONPATH=/code/adhoc-teaming python3 experiments/train.py --env lbf --type original --tag lbf_orig_v1 --algorithm mappo --steps 10000000
   ```

##### 2. Running experiments on augmented role based LBF environment
   ```
PYTHONPATH=/code/adhoc-teaming python3 experiments/train.py --env lbf --type original --tag lbf_roles_v1 --algorithm mappo --steps 10000000
   ```

##### 3. Running experiments on hybrid LBF environment
   ```
PYTHONPATH=/code/adhoc-teaming python3 experiments/train.py --env lbf --type original --tag lbf_hybrid_v1 --algorithm mappo --steps 10000000
   ```

Optionally set restore argumeent (-restore) if training fails

