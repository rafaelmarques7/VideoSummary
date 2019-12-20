import json

def write_text_to_file(data, fpath):
  with open(fpath, 'w') as f:
    f.write(data)
  return True

def write_json_to_file(data, fpath):
  with open(fpath, 'w') as f:
    json.dump(data, f)
  return True
