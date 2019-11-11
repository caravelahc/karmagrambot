from typing import List

from invoke import Result, UnexpectedExit, task


def check_all(results: List[Result]):
    try:
        result = next(result for result in results if result.exited != 0)
    except StopIteration:
        pass
    else:
        raise UnexpectedExit(result)


@task
def format(c):
    c.run('black -q karmagrambot')
    c.run('isort -rc -y -q karmagrambot')


@task
def format_check(c):
    check_all([
        c.run('black --check -q karmagrambot', warn=True),
        c.run('isort -rc -c -q karmagrambot', warn=True),
    ])
