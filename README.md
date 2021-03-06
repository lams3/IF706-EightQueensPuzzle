# IF706-EightQueensPuzzle
![Queen](./assets/queen.png)
An evolutionary approach to the eight queens puzzle.

### Running
1. Have **pipenv** installed in your machine. [Detailed instructions](https://pypi.org/project/pipenv/) depends on your platform.
2. Run `pipenv install`. (Installs all dependencies in a local [virtual environment](https://virtualenv.pypa.io/en/latest/))
3. Run `pipenv run python src/learn.py`. (or any other module)

### Type checking
Type check is being done with [mypy](https://mypy.readthedocs.io/en/stable/index.html). Make sure to have it installed (v0.761).  
Then, run `mypy src` in top level directory.

### Code formatter
Only commit code after running code formatter [yapf](https://github.com/google/yapf).  
Run `yapf src/ -ri`

### Observations
1. Run modules from top level directory through **pipenv**.

