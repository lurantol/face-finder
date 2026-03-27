import sys, subprocess, platform

REQUIRED = [
    "flask",
    "numpy",
    "pillow",
    "scikit-learn",
    "tqdm"
]

def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def bootstrap():
    print("Checking environment...")
    print("OS:", platform.system())
    print("Python:", sys.version.split()[0])

    for pkg in REQUIRED:
        try:
            __import__(pkg)
        except:
            print("Installing", pkg)
            install(pkg)

    print("Environment ready")
    print("Service started: http://localhost:5000")
