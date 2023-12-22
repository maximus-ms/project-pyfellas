import os
import shutil


project_name = "assistant"
project_util = "assistant"
project_author = "PyPellasBand"
project_description = "Personal assistant"
project_url = "https://github.com/maximus-ms/project-pyfellas"
project_files = (
    "BaseClasses.py",
    "Book.py",
    "Bot.py",
    "Contacts.py",
    "Notes.py",
    "main.py",
)
project_main = "main.py"
init_file = "__init__.py"

setup_file = "setup.py"
setup_content = """
from setuptools import setup

setup(name='{project_name}',
      version='{version}',
      description='{description}',
      url='{url}',
      author='{author}',
      license='MIT',
      packages=['{packages}'],
      install_requires={required_packages},
      entry_points={{'console_scripts': ['{project_util} = {project_name}.main:main']}})
"""


def rm_dir(directory_path):
    try:
        shutil.rmtree(directory_path)
        print(
            f"Directory '{directory_path}' and its contents deleted successfully."
        )
    except OSError as e:
        print(f"Error: {e}")


def create_directory(directory_path):
    if os.path.exists(directory_path):
        rm_dir(directory_path)
    os.makedirs(directory_path)


def copy_files(files_to_copy, destination_dir):
    for file_name in files_to_copy:
        source_file = file_name
        # source_file = os.path.join(source_directory, file_name)
        destination_file = os.path.join(destination_dir, file_name)
        shutil.copy2(source_file, destination_file)


package_setup_dir = os.path.join(project_name)
package_src_dir = os.path.join(package_setup_dir, project_name)
package_init_file = os.path.join(package_src_dir, init_file)
package_setup_file = os.path.join(package_setup_dir, setup_file)


def make_project():
    create_directory(package_setup_dir)
    create_directory(package_src_dir)
    copy_files(project_files, package_src_dir)
    with open(package_init_file, "w") as fd:
        fd.write("")

    list_of_modules = [x[:-3] for x in project_files]
    for file in project_files:
        src_file = os.path.join(package_src_dir, file)
        with open(src_file, "r") as fd:
            data = fd.read()
        for module in list_of_modules:
            data = data.replace(
                f"from {module} import", f"from {project_name}.{module} import"
            )
        with open(src_file, "w") as fd:
            fd.write(data)


def get_requirements():
    import subprocess

    good_message = "INFO: Successfully output requirements"
    try:
        cmd = ["pipreqs", package_src_dir, "--print"]
        pipe = subprocess.Popen(
            cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        cout = pipe.stdout
        output = cout.read()
        cout.close()
        rc = pipe.wait()
        text = output.decode().strip()
        if not good_message in text:
            print(text)
            return 0
        text = text.split(good_message)
        print(text[0])
        print(good_message)
        required_packages = text[1].strip().splitlines()
        for r in required_packages:
            print(r)
        return required_packages

        # print(str(output))
    except FileNotFoundError:
        print("pipreqs is not installed or not found. Please install pipreqs.")
    except Exception as e:
        print(f"An error occurred: {e}")
    exit(1)


def make_setup_file(required_packages):
    with open(package_setup_file, "w") as fd:
        fd.write(
            setup_content.format(
                project_name=project_name,
                version="1.0.0",
                description=project_description,
                url=project_url,
                author=project_author,
                packages=project_name,
                required_packages=required_packages,
                project_util=project_util,
            )
        )


if __name__ == "__main__":
    make_project()
    required_packages = get_requirements()
    make_setup_file(required_packages)

    print("Packet 'assistant' was successfully created")
    print("You can install it by 'pip install ./assistant'")
