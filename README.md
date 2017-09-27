# IRIDA SISTR Results

The IRIDA SISTR Results application enables the export of [SISTR][sistr-web] results that were run through [IRIDA][irida] (via the [sistr-cmd][sistr-cmd] application) to a spreadsheet. See the [IRIDA SISTR Pipeline][irida-sistr-pipeline] documentation for more details on the presentation of SISTR results in IRIDA.

# Quick Usage

To export SISTR results from IRIDA to a spreadsheet, please run the following:

```bash
irida-sistr-results.py -p 1 -p 2 -u irida-user -o out.xlsx
```

This will log into the configured IRIDA instance using the username `irida-user` and export SISTR results for the projects with IDs 1 and 2 to a file `out.xlsx`.  See the [IRIDA Projects][irida-projects] documentation for more details on projects.

Alternatively, instead of specifying individual projects you may use `-a` to export all projects.

```bash
irida-sistr-results.py -a -u irida-user -o out.xlsx
```

The exported file `out.xlsx` will look like the following:

![sistr-results-example.png][]

This will list each sample in the given projects, as well as the associated SISTR results. The **QC Status** column will list one of **PASS**, **WARNING**, **FAIL**, or **MISSING** depending on the status of the results.  In particular, **MISSING** represents a sample with a missing SISTR result.

In the case of multiple SISTR results per sample, IRIDA will load up that SISTR result which has a status of `PASS` that was run most recently for a particular sample.  To disable this behavior, please use `--exclude-user-existing-results`.


## Specify connection details

If the connection details to the IRIDA instance have not already been configured, then you may run this command as:

```bash
irida-sistr-results.py --irida-url [http://irida-url] --client-id [id] --client-secret [secret] -p 1 -p 2 -u irida-user -o out.xlsx
```

The connection details correspond to the details for an [IRIDA Client][irida-client] which you will need to have been provied.

## Include MISSING results

To include results for **MISSING** samples you must re-run the data for these results in IRIDA and re-export the results to a table. To re-run in IRIDA please select the samples in question ([selecting samples by a text file][select-by-file] may be useful here) and resubmit these samples to the [SISTR Pipeline][irida-sistr-pipeline]. If you wish all users in the project to have access to these results, please make sure to [Share pipeline results with a project][share-results-project].

# Installation

To get IRIDA SISTR Results, please run:

```bash
git clone https://github.com/phac-nml/irida-sistr-results.git
cd irida-sistr-results
```

## Dependencies

1. IRIDA `0.18.3`
   IRIDA SISTR Results requires an IRIDA version of at least `0.18.3` to work properly.  Please see the IRIDA [GitHub][irida-github-release] page for more details on releases.

2. Python dependencies
   IRIDA SISTR Results requires [Python 3][python-3]. A quick method to get Python 3 is to use [Miniconda 3][miniconda] (or alternatively, use Miniconda 2 and create an environment for Python 3 with run `conda create --name python-3 python=3; source activate python3`).

   Once the correct Python is installed, you may install the rest of the dependencies with:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Instead of providing all the configuration details on the command line, they can be specified in a configuration file.  This file can be placed either in `irida-sistr-results/conf/config.ini` or `~/.local/share/irida-sistr-results/config.ini`.

To quickly set up configuration, please run `cp conf/config.ini.example conf/config.ini` and fill in the information within the [config.ini][config] file (the `url`, `client_id`, and `client_secret` connection details).

# Usage

```
usage: irida-sistr-results.py [-h] [--irida-url IRIDA_URL]
                              [--client-id CLIENT_ID]
                              [--client-secret CLIENT_SECRET] [-u USERNAME]
                              [--password PASSWORD] [-v] [-p PROJECTS] [-a]
                              [--output-tab TABULAR_FILE] [-o EXCEL_FILE]
                              [--exclude-user-results]
                              [--exclude-user-existing-results] [-T TIMEOUT]
                              [-V]

Compile SISTR results from an IRIDA instance into a table.

optional arguments:
  -h, --help            show this help message and exit
  --irida-url IRIDA_URL
                        The URL to the IRIDA instance.
  --client-id CLIENT_ID
                        The client id for an IRIDA instance.
  --client-secret CLIENT_SECRET
                        The client secret for the IRIDA instance.
  -u USERNAME, --username USERNAME
                        The username for the IRIDA instance.
  --password PASSWORD   The password for the IRIDA instance. Prompts for password if left blank.
  -v, --verbose         Turn on verbose logging.
  -p PROJECTS, --project PROJECTS
                        Projects to scan for SISTR results. If left blank will scan all projects the user has access to.
  -a, --all-projects    Explicitly load results from all projects the user has access to.  Will ignore the values given in --project.
  --output-tab TABULAR_FILE, --to-tab-file TABULAR_FILE
                        Print results to tab-deliminited file.
  -o EXCEL_FILE, --output-excel EXCEL_FILE, --to-excel-file EXCEL_FILE
                        Print results to the given excel file.
  --exclude-user-results
                        Do not include SISTR analysis results run directly by the user (only include SISTR results automatically generated by IRIDA).
  --exclude-user-existing-results
                        If including user results, do not replace existing SISTR analysis that were automatically generated with user-run SISTR results.
  -T TIMEOUT, --connection-timeout TIMEOUT
                        Connection timeout when getting results from IRIDA.
  -V, --version         show program's version number and exit

Example:
	irida-sistr-results.py -a -u irida-user -o out.xlsx
		Exports all SISTR results from all projects to a file 'out.xlsx'

	irida-sistr-results.py -p 1 -p 2 -u irida-user -o out.xlsx
		Exports SISTR results form projects [1,2] to a file 'out.xlsx'
```

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
[irida-projects]: https://irida.corefacility.ca/documentation/user/user/project/
[irida-sistr-pipeline]: https://irida.corefacility.ca/documentation/user/user/sistr/
[irida-client]: http://irida.corefacility.ca/documentation/user/administrator/#managing-system-clients
[python-3]: https://www.python.org/
[miniconda]: https://conda.io/miniconda.html
[config]: conf/config.ini.example
[sistr-results-example.png]: images/sistr-results-example.png
[select-by-file]: https://irida.corefacility.ca/documentation/user/user/samples/#filtering-and-selecting-by-file
[share-results-project]: https://irida.corefacility.ca/documentation/user/user/pipelines/#sharing-pipeline-results
[irida-github-release]: https://github.com/phac-nml/irida/releases
