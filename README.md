# IRIDA SISTR Results

The IRIDA SISTR Results application enables the export of [SISTR][sistr-web] results that were run through [IRIDA][irida] (via the [sistr-cmd][sistr-cmd] application) to a spreadsheet.

# Usage

To export SISTR results from IRIDA to a spreadsheet, please run the following:

```bash
irida-sistr-results.py --project 1 --project 2 --username irida-user --to-excel-file out.xlsx
```

This will log into the configured IRIDA instance using the username `irida-user` and export SISTR results for project 1 and 2 to a file `out.xlsx` which will look like the following:

![sistr-results-example.png][]

This will list each sample in the given projects, as well as the associated SISTR results. The **QC Status** column will list one of **PASS**, **WARNING**, **FAIL**, or **MISSING** depending on the status of the results.  In particular, **MISSING** represents a sample with a missing SISTR result.

In the case of multiple SISTR results per sample, IRIDA will load up that SISTR result which has a status of `PASS` that was run most recently for a particular sample.  To disable this behavior, please use `--exclude-user-existing-results`.

## Specify connection details

If the connection details to the IRIDA instance have not already been configured, then you may run this command as:

```bash
irida-sistr-results.py --irida-url [http://irida-url] --client-id [id] --client-secret [secreet] --project 1 --project 2 --username irida-user --to-excel-file out.xlsx
```

The connection details correspond to the details for an [IRIDA Client][irida-client] which you will need to have been provied.

# Installation

To get IRIDA SISTR Results, please run:

```bash
git clone https://irida.corefacility.ca/irida/irida-sistr-results.git
cd irida-sistr-results
```

## Dependencies

IRIDA SISTR Results requires [Python 3][python-3]. A quick method to get Python 3 is to use [Miniconda 3][miniconda] (or alternatively, use Miniconda 2 and create an environment for Python 3 with run `conda create --name python-3 python=3; source activate python3`.

Once the correct Python is installed, you may install the rest of the dependencies with:

```bash
pip install -r requirements.txt
```

## Configuration

Instead of providing all the configuration details on the command line, they can be specified in a configuration file.  This file can be placed either in `irida-sistr-results/conf/config.ini` or `~/.local/share/irida-sistr-results/config.ini`.

To quickly set up configuration, please run `cp conf/config.ini.example conf/config.ini` and fill in the information within the [config.ini][config] file.

# Legal

Copyright 2017 Government of Canada

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this work except in compliance with the License. You may obtain a copy of the
License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

[sistr-web]: http://lfz.corefacility.ca/sistr-app/
[irida]: https://irida.ca
[sistr-cmd]: https://github.com/peterk87/sistr_cmd
[irida-client]: http://irida.corefacility.ca/documentation/user/administrator/#managing-system-clients
[python-3]: https://www.python.org/
[miniconda]: https://conda.io/miniconda.html
[config]: conf/config.ini.example
[sistr-results-example.png]: images/sistr-results-example.png
