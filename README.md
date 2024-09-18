# pyweek-sept-2024

# Installing the project for development

Hi dear contributors. This project uses the uv packet manager, I will personally guide you for the installation process.

1. Make sure to have a python version between 3.10 and 3.12 (inclusive, so 3.10 and 3.12 are ok as well)
2. Create a virtual environment and activate it (you can do this through python venv module or using uv as well)
3. Install uv if not already installed (`pip install uv`)
4. Install dependencies by running `uv sync`
5. Install pre-commit by running `pre-commit install`
6. Create a new git branch (don't work on your main) `git branch new_name`
7. Checkout to the new git branch `git checkout new_name`
8. To run the project execute this command `python src`
9. Remember to pick an issue from the gh repo. PUSH to main are disallowed, it'll error you. PRs and commits must be atomic.

Now you're ready to go! If you have any problem with the project contact me (Snipy7374)
