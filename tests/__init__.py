from execute import run


def test_execute():
    cwd = r"C:\Users\Ohad Cohen\PycharmProjects\pyci\tests"
    result = run("write.bat", console=True, cwd=cwd)
    print(result)


def test_git():
    from execute.git import get_info
    cwd = r"C:\Git\PyImage"
    res = get_info(cwd)
    # result = run("write.bat", console=True, cwd=cwd)
    print(res)


test_git()
"""
def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print output.strip()
    rc = process.poll()
    return rc
    """
