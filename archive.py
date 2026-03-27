import zipfile, tarfile

def extract(path, out):
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            z.extractall(out)
