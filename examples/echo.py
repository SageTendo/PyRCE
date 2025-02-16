def payload(self):
    import subprocess
    p = subprocess.run(["echo Hello world"], stdout=subprocess.PIPE, shell=True)
    return p.stdout.decode('utf-8')
