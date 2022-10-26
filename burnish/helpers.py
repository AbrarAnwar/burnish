import yaml
import burnish
# could import wandb to fit this framework
def import_yaml(yaml_path):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return_dict = burnish.util.create_grid_search(data)
    return return_dict
    
def import_csv(csv_file):
    pass