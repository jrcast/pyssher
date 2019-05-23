import setuptools

with open('requirements.txt') as f:
    reqs = f.read()

setuptools.setup(name='pyssher',
                 version="0.1.1",
                 description="pyssher: run commands in multiple ssh clients simultaneously",
                 author="jrcast",
                 author_email="jrcast@users.noreply.github.com",
                 packages=setuptools.find_packages(),
                 include_package_data=True,
                 url="https://github.com/jrcast/pyssher",
                 install_requires = (reqs.strip().split("\n"),),
                 entry_points={"console_scripts": ["pyssher=pyssher.pyssher:pyssher"]}
                 )
