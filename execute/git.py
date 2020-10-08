import re
import json
from execute import run
from execute.utils import write_log, get_most_exact


class GitProject(object):
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id", None)
        self.full_path = kwargs.get("full_path", None)
        self.full_name = kwargs.get("full_name", None)
        self.branch = kwargs.get("branch", None)
        self.parent = kwargs.get("parent", None)
        self.url = kwargs.get("url", None)
        self.head_hash = kwargs.get("head_hash", None)
        self.tag_hash = kwargs.get("tag_hash", None)
        self.last_tag = kwargs.get("last_tag", None)
        self.next_tag_hash = kwargs.get("next_tag_hash", None)
        self.next_tag = kwargs.get("next_tag", None)
        self.short_summary = kwargs.get("short_summary", None)
        self.detailed_summary = kwargs.get("detailed_summary", None)
        self.submodules = kwargs.get("submodules", [])
        self.status = kwargs.get("status", "freeze")

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class GitSubmodule(GitProject):
    def __init__(self, *args, **kwargs):
        super(GitSubmodule, self).__init__(*args, **kwargs)
        self.name = kwargs.get("name", None)
        self.path = kwargs.get("path", None)
        self.relative_url = kwargs.get("relative_url", None)


def run_git(cmd, console=False, cwd=None, log_file=None, check_output=False, timeout_sec=20):
    result = run(cmd, output_path=log_file, console=console, check_output=check_output, timeout_sec=timeout_sec,
                 cwd=cwd)
    output = result.get_output()
    write_log(log_file, output, console=False)  # maybe can leave it to execute
    return result


def get_head_hash(cwd=None):
    return str(run_git("git log --format=\"%H\" -n 1", cwd=cwd).get_output_lines()[-1]).replace("\"", "")


def get_tag_hash(tag, cwd=None):
    if tag is not None:
        return run_git("git rev-list {} --max-count=1 --".format(tag), cwd=cwd).get_output_lines()[-1]
    else:
        return tag


def get_project_url(cwd):
    return run_git("git config remote.origin.url", cwd=cwd).get_output_lines()[-1]


def get_project_full_name(project_url):
    project_name = None
    project_name_match = re.match(r'(?:ssh|http|https)://.*(?:(?::\d*)|(?:\.\w{3}))/(.*)', project_url)
    if project_name_match is not None:
        project_name = project_name_match.group(1)
        project_name = project_name.rstrip(".git")

    return project_name


def get_tag_date(cwd, tag):
    return run_git('git log -1 --format=%ai {}'.format(tag), cwd=cwd).get_output_lines()[-1]


def has_git_changes(cwd):
    result = run_git("git status", cwd=cwd)
    output = result.get_output()
    return "nothing to commit, working tree clean" not in output


def get_last_tag(cwd=None):
    last_tag = None
    all_tags = run_git('git tag --list', cwd=cwd).get_output_lines()
    if len(all_tags) > 0:
        last_tag = run_git('git describe --abbrev=0', cwd=cwd).get_output_lines()[-1]
    return last_tag


def get_branch(current_hash=None, last_tag=None, cwd=None):
    result = None

    if current_hash is not None:
        cmd_result = run_git('git branch -a --contains \"{}\"'.format(current_hash), cwd=cwd,
                             timeout_sec=60)
        result = cmd_result.get_output_lines()
        result = result[1:]
        only_branches = [str(b[str(b).rfind("/") + 1:]).replace("/", "").strip(" *") for b in result if b]
        unique_branches = list(set(only_branches))
        unique_branches = [b for b in unique_branches if "detached from" not in b]
        if len(unique_branches) == 1:
            return unique_branches[0]
        elif last_tag is not None:
            result = get_most_exact(unique_branches, last_tag)
        else:
            return unique_branches[0]

    return result


def resolve_tag_on_remote(cwd, log_file, fix=True):
    pass


def get_info(cwd):
    project = GitProject()
    project.url = get_project_url(cwd=cwd)
    project.head_hash = get_head_hash(cwd=cwd)
    project.full_path = cwd
    project.branch = get_branch(project.head_hash, cwd=cwd)
    project.full_name = get_project_full_name(project.url)
    return project
