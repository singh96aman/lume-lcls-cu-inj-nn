from setuptools import setup, find_packages
from os import path
import versioneer

cur_dir = path.abspath(path.dirname(__file__))

# parse requirements
with open(path.join(cur_dir, "requirements.txt"), "r") as f:
    requirements = f.read().split()

setup(
    name="lume_lcls_cu_inj_nn",
    author="Jacqueline Garrahan",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    #  license="...",
    install_requires=requirements,
    url="https://github.com/jacquelinegarrahan/lume-lcls-cu-inj-nn",
    include_package_data=True,
    python_requires=">=3.8",
    entry_points={
        "orchestration": [
            "lume_lcls_cu_inj_nn.model=\
                lume_lcls_cu_inj_nn.model:LumeLclsCuInjNn",
            "lume_lcls_cu_inj_nn.flow=\
                lume_lcls_cu_inj_nn.flow:flow",
        ]
    },
)
