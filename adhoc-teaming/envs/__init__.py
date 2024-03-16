from marllib.envs.base_env import ENV_REGISTRY
from .lbf_roles import RLlibLBFRoles
ENV_REGISTRY["lbfroles"] = RLlibLBFRoles
