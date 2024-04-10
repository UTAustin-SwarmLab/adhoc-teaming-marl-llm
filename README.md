

## Starting a container
docker image build --platform linux/amd64 -t  ubuntu20.04:cuda-11.3-torch-1.11 .

docker container create -it --name teaming --gpus 4 -p 8080:8080 -v /Users/hg22723/Phd/Research/P2-AdHocTeaming/adhoc-teaming-marl-llm:/code/   ubuntu20.04:cuda-11.3-torch-1.11



