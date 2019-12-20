def write_to_file(data, fpath):
  with open(fpath, 'w') as f:
    f.write(data)
  return True
