import setuptools

with open('readme.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='redirect_detector',
    version='0.0.1',
    author_email='wreckah@ya.ru',
    description='Resolver of redirects chain',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)
