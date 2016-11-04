import os
import json
import argparse

class Data(object):

    def __init__(self, list_of_items):
        self.list_of_items = list_of_items
        self.data_by_id = { d['identifier'] : d for d in list_of_items }

    def matching_condition(self, variable, value):
        ids = []

        for datum in self.list_of_items:
            if datum[variable] == value:
                ids.append(datum['identifier'])

        return ids

    def by_id(self, id):
        return self.data_by_id[id]

def sanitise_filename(filename):

    def escape_char(input_string, char):
        return input_string.replace(char, '\\'+char)

    sanitised = escape_char(filename, ' ')
    sanitised = escape_char(sanitised, '(')
    sanitised = escape_char(sanitised, ')')

    return sanitised

def get_false_color_filenames(project_root, datum):

    filename = os.path.join(project_root, 'output', datum['identifier'] + '-false_color.png')

    return filename
    
def get_original_filenames(project_root, datum):

    filename = os.path.join(project_root, 'raw', datum['relative_raw_path'])

    return sanitise_filename(filename)

def summarise_results(raw_data_manifest, analysis_root):

    for datum in raw_data_manifest.list_of_items:
        identifier = datum['identifier']
        print identifier

def load_manifest(project_root):

    manifest_filename = os.path.join(project_root, 'manifest.json')

    with open(manifest_filename) as f:
        manifest_json = json.load(f)

    data = Data(manifest_json)

    return data

def show_files_for_a_plot():
    # BROKEN

    identifiers = data.matching_condition('plot_index', 1)

    originals = []
    false_colored = []
    for identifier in identifiers:
       datum = data.by_id(identifier)
       false_colored.append(get_false_color_filenames(project_root, datum))

    print('\n'.join(false_colored))


def main():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('project_root', help='Root of project directory.')
    parser.add_argument('analysis_name', help='Identifier for analysis.')

    args = parser.parse_args()

    manifest_data = load_manifest(args.project_root)

    results_root = os.path.join(args.project_root, 'output', args.analysis_name)
    summarise_results(manifest_data, results_root)

if __name__ == "__main__":
    main()
