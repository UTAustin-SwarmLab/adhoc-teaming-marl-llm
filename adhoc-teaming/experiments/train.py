'''Runs both the training and evaluation for any given environment'''




from marllib import marl
from envs import *
from argparse import ArgumentParser
import yaml
import os
from envs import *

def parse_args():
    parser = ArgumentParser(description='Image Classification with CLIP')

    parser.add_argument(
        '--env',
        choices=['lbf'],
        default='lbf',
        help='Environment to train on')

    parser.add_argument(
        '--roles',
        default=False,
        action='store_true',
        help='Whether to use original version or roles version of the environment')
    
    parser.add_argument(
        '--tag',
        default='v1',
        help='Tag for the experiment')
    return  parser.parse_args()
    
    
if __name__ == '__main__':
    
    args = parse_args()
    
    if args.env == 'lbf':
        env_name = 'lbf' if not args.roles else 'lbfroles'
        print("Using environment: ", env_name)
        config_path = 'experiments/lbf_config.yaml'
        
        with open(config_path, "r") as f:
            yaml_file = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
        
        print(yaml_file)
        env_config = yaml_file['env_args']
        map_name = env_config['map_name'] + args.tag
        
    
    # initialize env
    config_path = os.path.join("../../", config_path)
    env = marl.make_env(environment_name=env_name, 
                        map_name=map_name,
                        abs_path=config_path)
    # pick mappo algorithms
    mappo = marl.algos.mappo(hyperparam_source="test")
    # customize model
    model = marl.build_model(env, mappo, {"core_arch": "mlp", "encode_layer": "128-128"})
    # start learning
    mappo.fit(env, model, stop={'timesteps_total': 10000000},
              local_mode=True, 
              num_gpus=1,
              num_workers=16,
              share_policy='all',
              checkpoint_freq=50)