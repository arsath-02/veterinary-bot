import os

def load_and_preprocess_data(folder):
    data = {}
    for species in os.listdir(folder):
        species_folder = os.path.join(folder, species)
        data[species] = []
        for file in os.listdir(species_folder):
            with open(os.path.join(species_folder, file), 'r') as f:
                data[species].append(f.read())
    return data

data = load_and_preprocess_data("data")
