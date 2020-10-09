import re
import os
import json
from execute import run
from execute.utils import write_log, get_most_exact, index_of, try_parse_int, fix_path


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
    """
    Executes a command to get the hash of head (last commit in local repo)
    :param cwd the working directory of the git repo
    :return: the last commit hash
    """
    return str(run_git("git log --format=\"%H\" -n 1", cwd=cwd).get_output_lines()[-1]).replace("\"", "")


def get_tag_hash(tag, cwd=None):
    """
    Executes a command that gets the given tag hash
    :param tag: the tag we want to get the hash for
    :param cwd the working directory of the git repo
    :return: the hash of the given tag
    """
    if tag is not None:
        return run_git("git rev-list {} --max-count=1 --".format(tag), cwd=cwd).get_output_lines()[-1]
    else:
        return tag


def get_project_url(cwd):
    """
    Executes a command that gets the url of the current repo (tested only with on-premise git server)
    :param cwd the working directory of the git repo
    :return: the url of the project
    """
    return run_git("git config remote.origin.url", cwd=cwd).get_output_lines()[-1]


def get_project_full_name(project_url):
    """
    Gets the project full name based on the project url
    :param project_url: the project url
    :return: the project full name (e.g. <user/folder>/<*>/<project name>
    """
    project_name = None
    project_name_match = re.match(r'(?:ssh|http|https)://.*(?:(?::\d*)|(?:\.\w{3}))/(.*)', project_url)
    if project_name_match is not None:
        project_name = project_name_match.group(1)
        project_name = project_name.rstrip(".git")

    return project_name


def get_tag_date(cwd, tag):
    """
    Gets the given tag date
    :param cwd: the git project directory
    :param tag: the requested tag to get date for
    :return: the date as str
    """
    return run_git('git log -1 --format=%ai {}'.format(tag), cwd=cwd).get_output_lines()[-1]


def has_git_changes(cwd):
    """
    Runs git status in the given path
    :param cwd: the full path to the git project
    :return: True if there are changes to commit and False otherwise
    """
    result = run_git("git status", cwd=cwd)
    output = result.get_output()
    return "nothing to commit, working tree clean" not in output


def get_last_tag(cwd=None):
    """
    Executes a command to get last annotated tag of current repo (implied by cwd)
    :param cwd the git project directory
    :return: the last annotated tag, None if couldn't find
    """
    last_tag = None
    all_tags = run_git('git tag --list', cwd=cwd).get_output_lines()
    if len(all_tags) > 0:
        last_tag = run_git('git describe --abbrev=0', cwd=cwd).get_output_lines()[-1]
    return last_tag


def get_branch(current_hash=None, last_tag=None, cwd=None):
    """
    Gets the branch name of the current commit in the project directory
    :param current_hash: the hash of 'HEAD' in the current project
    :param last_tag: the last tag we found
    :param cwd: the git project directory
    :return: the branch name on which our project is set
    """
    result = None

    if current_hash is not None:
        cmd_result = run_git('git branch -a --contains \"{}\"'.format(current_hash), cwd=cwd,
                             timeout_sec=60)
        result = cmd_result.get_output_lines(exclude_command=True, exclude_cwd=True)
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


def resolve_tag_on_remote(cwd, log_file, fix=False):
    """
    Makes sure that the last tag is not present on git, if it does - delete it
    :param log_file: the log file to write to
    :param cwd: the working directory of the git project
    :param fix whether to fix the tag by removing local tag
    :return:
    """
    local_tag = get_last_tag(cwd)
    if fix:
        i_tag, i_counter = local_tag.rsplit("_", 1)
        remote_tags_result = run_git("git ls-remote --tags origin --pattern {}*".format(i_tag), cwd=cwd)
        output_lines = remote_tags_result.get_output_lines()

        namespace = "refs/tags/"
        remote_tags = []
        for line in output_lines:
            tag_end_index = line.rfind("^{}")
            if tag_end_index == -1:
                tag_end_index = len(line)
            result = line[line.rfind(namespace) + len(namespace):tag_end_index]
            if result not in remote_tags:
                remote_tags.append(result)

        local_tag_index = index_of(remote_tags, local_tag)
        if local_tag_index == -1:
            write_log(log_file, "Deleting local tag called {} ({})since its not on remote".format(local_tag,
                                                                                                  get_tag_hash(
                                                                                                      local_tag, cwd)))
            run_git("git tag -d {}".format(local_tag), cwd=cwd)
        else:
            if local_tag_index < (len(remote_tags) - 1):
                local_tag_body, local_tag_counter = local_tag.rsplit("_", 1)
                local_tag_counter = int(local_tag_counter)
                for idx in range(local_tag_index, len(remote_tags)):
                    i_tag, i_counter = remote_tags[idx].rsplit("_", 1)
                    i_counter, parsed = try_parse_int(i_counter)
                    if parsed and local_tag_body == i_tag and local_tag_counter < i_counter:
                        local_tag = remote_tags[idx]

    return local_tag


def get_next_tag(current_tag):
    next_tag = None
    if current_tag is not None:
        tag_body, tag_counter = current_tag.rsplit("_", 1)
        tag_counter = int(tag_counter) + 1
        tag_counter_len = 3 if len(str(tag_counter)) < 3 else len(str(tag_counter))
        next_tag = "{}_{}".format(tag_body, '{number:0{width}d}'.format(number=tag_counter, width=tag_counter_len))

    return next_tag


def get_submodules_from_gitmodules(cwd):
    """
    Fills submodules info from .gitmodules file.
    must have full_path to keep processing submodule data
    :param cwd: the directory of the parent project
    :return: a list of GitSubmodule
    """
    git_modules_path = "{}{}{}".format(cwd.rstrip(os.path.sep), os.path.sep, ".gitmodules")
    submodules = []
    if os.path.exists(git_modules_path) and os.path.isfile(git_modules_path):
        with open(git_modules_path, 'r') as git_modules:
            can_read = False
            submodule = None
            for line in git_modules:
                if "submodule" in line:
                    can_read = not line.strip().startswith("#")
                    if can_read:
                        if submodule is not None:
                            submodules.append(submodule)

                        submodule = GitSubmodule()
                        name_match = re.match('.*\"(.*)\".*', line, re.IGNORECASE)
                        if name_match is not None:
                            submodule.name = name_match.group(1).strip()
                elif can_read:
                    path_match = re.match('.*path.*=(.*)', line, re.IGNORECASE)
                    if path_match is not None:
                        submodule.path = path_match.group(1).strip()
                        submodule.full_path = os.path.join(cwd, fix_path(submodule.path))
                    else:
                        url_match = re.match('.*url.*=(.*)', line, re.IGNORECASE)
                        if url_match is not None:
                            submodule.relative_url = url_match.group(1).strip()

            if submodule is not None:
                if len(submodules) == 0 or submodules[-1] != submodule:
                    submodules.append(submodule)

    return submodules


def collect_git_info(git_project, parent_project=None):
    if isinstance(git_project, GitProject):
        git_project.url = get_project_url(cwd=git_project.full_path)
        git_project.head_hash = get_head_hash(cwd=git_project.full_path)
        git_project.full_name = get_project_full_name(git_project.url)
        git_project.last_tag = get_last_tag(cwd=git_project.full_path)
        git_project.tag_hash = get_tag_hash(git_project.last_tag, git_project.full_path)
        git_project.branch = get_branch(git_project.head_hash, cwd=git_project.full_path)
        git_project.id = "{}{}".format("{}/".format(parent_project.id) if parent_project is not None else "",
                                       git_project.full_name)
        git_project.parent = None if parent_project is None else parent_project.full_name
        submodules = get_submodules_from_gitmodules(git_project.full_path)
        for module in submodules:
            collect_git_info(module, git_project)
        git_project.submodules = submodules


def get_info(cwd):
    if cwd is None:
        # if cwd is not given, assume the caller is at the project directory
        cwd = os.path.abspath(os.getcwd())
    project = GitProject()
    project.full_path = cwd
    collect_git_info(project, None)
    return project
