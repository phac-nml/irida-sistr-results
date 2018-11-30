[![Build Status](https://travis-ci.org/phac-nml/irida-sistr-results.svg?branch=development)](https://travis-ci.org/phac-nml/irida-sistr-results)
[![pypi](https://badge.fury.io/py/irida-sistr-results.svg)](https://pypi.python.org/pypi/irida-sistr-results/)
[![conda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg)](https://anaconda.org/bioconda/irida-sistr-results)

# IRIDA SISTR Results

The IRIDA SISTR Results application enables the export of [SISTR][sistr-web] results that were run through [IRIDA][irida] (via the [sistr-cmd][sistr-cmd] application) to a spreadsheet. See the [IRIDA SISTR Pipeline][irida-sistr-pipeline] documentation for more details on the presentation of SISTR results in IRIDA.

# Quick Usage

To export SISTR results from IRIDA to a spreadsheet, please run the following:

```bash
irida-sistr-results -p 1 -p 2 -u irida-user -o out.xlsx
```

This will log into the configured IRIDA instance using the username `irida-user` and export SISTR results for the projects with IDs 1 and 2 to a file `out.xlsx`.  See the [IRIDA Projects][irida-projects] documentation for more details on projects.

Alternatively, instead of specifying individual projects you may use `-a` to export all projects.

```bash
irida-sistr-results -a -u irida-user -o out.xlsx
```

The exported file `out.xlsx` will look like the following:

![sistr-results-example.png][]

This will list each sample in the given projects, as well as the associated SISTR results. The **QC Status** column will list one of **PASS**, **WARNING**, **FAIL**, or **MISSING** depending on the status of the results.  In particular, **MISSING** represents a sample with a missing SISTR result.

In the case of multiple SISTR results per sample, IRIDA will load up that SISTR result which has a status of `PASS` that was run most recently for a particular sample.  To disable this behavior, please use `--exclude-user-existing-results`.

## Specify connection details

If the connection details to the IRIDA instance have not already been configured, then you may run this command as:

```bash
irida-sistr-results --irida-url [http://irida-url] --client-id [id] --client-secret [secret] -p 1 -p 2 -u irida-user -o out.xlsx
```

The connection details correspond to the details for an [IRIDA Client][irida-client] which you will need to have been provied.

## Include MISSING results

To include results for **MISSING** samples you must re-run the data for these results in IRIDA and re-export the results to a table. To re-run in IRIDA please select the samples in question ([selecting samples by a text file][select-by-file] may be useful here) and resubmit these samples to the [SISTR Pipeline][irida-sistr-pipeline]. Please make sure to [Share pipeline results with a project][share-results-project], or you will not see the results.

## Only include results from particular IRIDA/SISTR workflow verison

You may restrict results to only come from a particular IRIDA/SISTR workflow version. For example:

```bash
irida-sistr-results -p 1 -w 0.3 -w 0.2 -u irida-user -o out.xlsx
```

This will list each sample in project **1**, only including those results from the SISTR workflow versions `0.3` or `0.2`.

By default, results will come from any workflow version. A list of possible versions is shown when running `irida-sistr-results -h`.

```
  -w WORKFLOW_VERSIONS_OR_IDS, --workflow WORKFLOW_VERSIONS_OR_IDS
                        Only include results of these workflow versions (or uuids) ['0.1', '0.2', '0.3'] [all versions]
```

You may also pass the workflow UUID to `--workflow` instead of the version.

## Only include results from samples within a particular time period

You may restrict results to only come from a particular number of days ago using `-d|--samples-created-since`.  For example:

```bash
irida-sistr-results -p 1 -d 7 -u irida-user -o out.xlsx
```

This will export results from project 1, only exporting those results from samples created in the past 7 days.

```bash
irida-sistr-results -p 1 -d 2018-01-02 -u irida-user -o out.xlsx
```

This will export results from project 1, only exporting those results from samples created since January 2, 2018.

## Reportable Serovar Status column

By default, the results will include a **Reportable Serovar Status** column, indicating which sample is part of a subset of serovars able to be reported.

![reportable-serovar-table.png][]

The list of serovars considered as **reportable** is derived from the file [reportable_serovars.tsv][]. You can override this file with `--reportable-serovars-file`.

```
irida-sistr-results -p 1 -u irida-user --reportable-serovars-file serovars-file.tsv -o out.xlsx
```

You can also disable the inclusion of this column in your results with `--exclude-reportable-status`.

```
irida-sistr-results -p 1 -u irida-user --exclude-reportable-status -o out.xlsx
```

# Installation

## Bioconda

The easiest way to get IRIDA SISTR Results is through [Bioconda][]:

```
conda install -c bioconda irida-sistr-results
```

## PyPI/Pip

You can also install `irida-sistr-results` from [PyPI][pypi-irida] using `pip`:

```bash
pip install irida-sistr-results
```

## Latest code

Alternatively, if you wish to install the latest code from GitHub, please run:

```bash
pip install git+https://github.com/phac-nml/irida-sistr-results
```

## Dependencies

* Python 3
* IRIDA `>=0.18.3`

    IRIDA SISTR Results requires an IRIDA version of at least `0.18.3` to work properly.  Please see the IRIDA [GitHub][irida-github-release] page for more details on releases.

## Configuration

Instead of providing all the configuration details on the command line, they can be specified in a configuration file.  This file can be placed in `~/.local/share/irida-sistr-results/config.ini`, or passed on the command-line (using `--config`).

To quickly set up configuration, please run `irida-sistr-results` once to copy a template to `~/.local/share/irida-sistr-results/config.ini` and fill in the information within the [config.ini][config] file (the `url`, `client_id`, and `client_secret` connection details).

To see a list of all locations where you can place the `config.ini` file, you may check the usage statement for the `-c, --config` information.  E.g.,

```
irida-sistr-results | grep '^ *-c' -A 1
    Configuration file for IRIDA (overrides values in ['/path1/config.ini', '/path2/config.ini'])
```

# Usage

```
usage: irida-sistr-results [-h] [--irida-url IRIDA_URL]
                           [--client-id CLIENT_ID]
                           [--client-secret CLIENT_SECRET] [-u USERNAME]
                           [--password PASSWORD] [-v] [-p PROJECTS] [-a]
                           [--output-tab TABULAR_FILE] [-o EXCEL_FILE]
                           [--include-user-results]
                           [--exclude-user-existing-results]
                           [--reportable-serovars-file REPORTABLE_SEROVARS_FILE]
                           [--exclude-reportable-status] [-T TIMEOUT]
                           [-c CONFIG] [-V] [-w WORKFLOW_VERSIONS_OR_IDS]
                           [-d SAMPLES_CREATED_SINCE]

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
  -a, --all-projects    Explicitly load results from all projects the user has access to.  Will ignore the values given 
                        in --project.
  --output-tab TABULAR_FILE, --to-tab-file TABULAR_FILE
                        Print results to tab-deliminited file.
  -o EXCEL_FILE, --output-excel EXCEL_FILE, --to-excel-file EXCEL_FILE
                        Print results to the given excel file.
  --include-user-results
                        Include SISTR analysis results run directly by the user.
  --exclude-user-existing-results
                        If including user results, do not replace existing SISTR analysis that were automatically
                        generated with user-run SISTR results.
  --reportable-serovars-file REPORTABLE_SEROVARS_FILE
                        The reportable serovars file [irida_sistr_results/data/reportable_serovars.tsv].
  --exclude-reportable-status
                        Excludes printing of reportable serovar status in final output.
  -T TIMEOUT, --connection-timeout TIMEOUT
                        Connection timeout when getting results from IRIDA.
  -c CONFIG, --config CONFIG
                        Configuration file for IRIDA (overrides values in ['irida_sistr_results/etc/config.ini',
                        '.local/share/irida-sistr-results/config.ini'])
  -V, --version         show program's version number and exit
  -w WORKFLOW_VERSIONS_OR_IDS, --workflow WORKFLOW_VERSIONS_OR_IDS
                        Only include results of these workflow versions (or uuids) ['0.1', '0.2', '0.3'] [all versions]
  -d SAMPLES_CREATED_SINCE, --samples-created-since SAMPLES_CREATED_SINCE
                        Only include samples created more recently than this date (in format YYYY-MM-DD) or this many days ago (as a number) [Include all samples]

Example:
        irida-sistr-results -a -u irida-user -o out.xlsx
                Exports all SISTR results from all projects to a file 'out.xlsx'

        irida-sistr-results -p 1 -p 2 -u irida-user -o out.xlsx
                Exports SISTR results from projects [1,2] to a file 'out.xlsx'

        irida-sistr-results -p 1 -w 0.3 -w 0.2 -u irida-user -o out.xlsx
                Exports only SISTR results from workflow versions 0.3 and 0.2 from project [1]
```

# Legal

Copyright 2018 Government of Canada

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
[Bioconda]: https://bioconda.github.io/
[sistr-cmd]: https://github.com/peterk87/sistr_cmd
[irida-projects]: https://irida.corefacility.ca/documentation/user/user/project/
[irida-sistr-pipeline]: https://irida.corefacility.ca/documentation/user/user/sistr/
[irida-client]: http://irida.corefacility.ca/documentation/user/administrator/#managing-system-clients
[python-3]: https://www.python.org/
[miniconda]: https://conda.io/miniconda.html
[config]: irida_sistr_results/etc/config.ini.example
[sistr-results-example.png]: images/sistr-results-example.png
[select-by-file]: https://irida.corefacility.ca/documentation/user/user/samples/#filtering-and-selecting-by-file
[share-results-project]: https://irida.corefacility.ca/documentation/user/user/pipelines/#sharing-pipeline-results
[irida-github-release]: https://github.com/phac-nml/irida/releases
[pypi-irida]: https://pypi.python.org/pypi/irida-sistr-results/
[reportable-serovar-table.png]: images/reportable-serovar-table.png
[reportable_serovars.tsv]: irida_sistr_results/data/reportable_serovars.tsv

