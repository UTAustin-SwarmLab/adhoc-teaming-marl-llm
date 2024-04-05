'''Runs both the training and evaluation for any given environment'''




from marllib import marl
from envs import *
from argparse import ArgumentParser
import yaml
import os
from envs import *
import ray

def parse_args():
    parser = ArgumentParser(description='Image Classification with CLIP')

    parser.add_argument(
        '--env',
        choices=['lbf'],
        default='lbf',
        help='Environment to train on')

    parser.add_argument(
        '--type',
        default=False,
        choices=['original', 'roles', 'hybrid'],
        help='Whether to use original version or roles or hybrid version of the environment')

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
    parser.add_argument(
        '--steps',
        default=10000000,
        type=int,
        help='Number of steps to train the model')
    
    
    return  parser.parse_args()
    

def run_training(args):
    if args.env == 'lbf':
        env_name = 'lbf' if not args.roles else 'lbfroles'
        print("Using environment: ", env_name)
        if args.type == 'original':
            config_path = 'experiments/lbf_config.yaml'
        elif args.type == 'roles':
            config_path = 'experiments/lbf_roles_config.yaml'
        elif args.type == 'hybrid':
            config_path = 'experiments/lbf_hybrid_config.yaml'
        
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
    
    restore_path = {
                'params_path': '',  # experiment configuration
                'model_path': ''
            }
    if args.restore:   
        run_name = '_'.join([args.algorithm, model_arch, map_name])
        run_folder = os.path.join('exp_results', run_name)
        recent_checkpoint = None

        if not os.path.exists(run_folder):
            raise FileNotFoundError("No checkpoint found {}, Only {} available".\
                format(run_folder, os.listdir('exp_results')))
        else:
            params_path = None
            model_path = None
            for run in os.listdir(run_folder):
                run_ckpt_folder = os.path.join(run_folder, run)
                if not os.path.isdir(run_ckpt_folder):
                    continue
                print("Peeking into run: ", run_ckpt_folder)
                ckpts = filter(lambda f: os.path.isdir(os.path.join(run_ckpt_folder, f)),
                                        os.listdir(run_ckpt_folder))
                
                ckpts = list(filter(lambda f: f.startswith('checkpoint_'), ckpts))
                if len(ckpts) == 0:
                    continue
                ckpts_num = list(map(lambda f: (int(f.split('_')[1]),f), ckpts))

                cp_num = max(ckpts_num, key=lambda x: x[0])
                print("Checkpoint number: ", cp_num)
                if recent_checkpoint is None or cp_num[0] > recent_checkpoint[0]:
                    recent_checkpoint = cp_num
                    params_path = os.path.join(run_ckpt_folder, 'params.json')
                    model_path = os.path.join(run_ckpt_folder, 
                                              recent_checkpoint[1],
                                              'checkpoint-{}'.format(cp_num[0]))

            if params_path is None or model_path is None:
                raise FileNotFoundError("No checkpoint found in {}, Only {} available".\
                    format(run_folder, os.listdir(run_folder)))
            restore_path={
                'params_path': params_path,  # experiment configuration
                'model_path': model_path
            }
            
            print("Restoring from checkpoint: ", restore_path)
            import time
    
    if args.algorithm == 'mappo':
        
        # pick mappo algorithms
        algorithm = marl.algos.mappo(hyperparam_source="test") 
            # customize model
        model = marl.build_model(env, algorithm, {"core_arch": model_arch,
                                          "encode_layer": model_enc_layers})  
        algorithm.fit(env, model, stop={'timesteps_total': args.steps},
                local_mode=True, 
                restore_path=restore_path,
                num_gpus=1,
                num_workers=8,
                share_policy='all',
                checkpoint_freq=50)
    else:
        raise NotImplementedError("Algorithm not supported yet")
    
    
if __name__ == '__main__':
    
    args = parse_args()
    
    flag = False
    
    while not flag:
        try:
            if ray.is_initialized():
               ray.shutdown() 
            run_training(args)
            flag = True
        except Exception as e:
            print(e)
            print("Training failed: Restarting and Restoring...")
            args.restore = True
            ray.shutdown()
            while ray.is_initialized():
                import time
                time.sleep(5)
            
    
    