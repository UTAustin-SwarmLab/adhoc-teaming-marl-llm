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
    
    parser.add_argument(
        '--restore',
        default=False,
        action='store_true',
        help='Whether to restore training or not')
    
    parser.add_argument(
        '--algorithm',
        default='mappo',
        choices=['mappo', 'coma', 'qmix'],
        help='Model architecture to use')
    
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
        model_arch = yaml_file['model_params']['arch']
        model_enc_layers = yaml_file['model_params']['encode_layer']
    

        
    
    # initialize env
    config_path = os.path.join("../../", config_path)
    env = marl.make_env(environment_name=env_name, 
                        map_name=map_name,
                        abs_path=config_path)
    
    # start learning
    
    if args.restore:   
        run_name = '_'.join([args.algorithm, model_arch, map_name, args.tag])
        run_folder = os.path.join('exp_results', run_name)
        recent_checkpoint = None
        if not os.path.exists(run_folder):
            raise FileNotFoundError("No checkpoint found {}, Only {} available".\
                format(run_folder, os.listdir('exp_results')))
        else:
            for run in os.listdir(run_folder):
                last_ckpt = os.listdir(run)[-1]
                cp_num = int(last_ckpt.split('-')[1])
                if recent_checkpoint is None or cp_num > recent_checkpoint:
                    recent_checkpoint = cp_num
                    params_path = os.path.join(run_name, 'params.json')
                    model_path = os.path.join(run_name, f'checkpoint-{recent_checkpoint}')

            restore_path={
                'params_path': params_path,  # experiment configuration
                'model_path': model_path
            }
            
            print("Restoring from checkpoint: ", restore_path)
            import time
            time.sleep(1000)
    
    if args.algorithm == 'mappo':
        
        # pick mappo algorithms
        algorithm = marl.algos.mappo(hyperparam_source="test") 
            # customize model
        model = marl.build_model(env, algorithm, {"core_arch": model_arch,
                                          "encode_layer": model_enc_layers})    
        algorithm.fit(env, model, stop={'timesteps_total': 10000000},
                local_mode=True, 
                num_gpus=1,
                num_workers=16,
                share_policy='all',
                checkpoint_freq=50)
    else:
        raise NotImplementedError("Algorithm not supported yet")