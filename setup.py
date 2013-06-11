from setuptools import setup, find_packages

setup(name='django-api-auth',
      version='0.3',
      packages=find_packages(),
      description='django-api-auth leverages tokens for authentication and was built for use with the Angular HTTP Auth Interceptor',
      author='Chris Ridenour',
      author_email='chrisridenour@gmail.com',
      url='http://github.com/cridenour/django-api-auth',
      include_package_data=True,
      zip_safe=False,
      license='MIT',
)
