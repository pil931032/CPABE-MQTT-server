import yaml

# Load Setting
def load_attributes():
    with open('attribute.yaml', 'r') as f:
        return yaml.safe_load(f)

#Main
if __name__ == '__main__':
    print(load_attributes())