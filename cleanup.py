import os 
import shutil 

def clean(dir):
    for each in os.listdir(dir):
        each = os.path.join(dir, each)
        if 'cache' in each:
            try:
                shutil.rmtree(each)
            except:
                pass
        elif os.path.isdir(each) and 'cache' not in each:
            clean(each)

if __name__ == "__main__":
    try:
        shutil.rmtree('build')
    except:
        pass 
    try:
        shutil.rmtree('dist')
    except:
        pass 
    try:
        shutil.rmtree('rsHRF.egg-info')
    except:
        pass
    clean(os.getcwd())