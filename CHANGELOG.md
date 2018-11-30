# Version 0.6.0 (in development)

* Added additional column to report **Reportable Serovar Status** used to indicate serovars that are considered as reportable by SISTR.
    * Disable with `--exclude-reportable-status`. Override list of reportable serovars with `--reportable-serovars-file`.
* Saving the command-line string to the exported file.

# Version 0.5.0

* Changed code to conform better to Python packaging standards.
* Moved location of `config.ini` file so it gets properly included in Python package.
* Add command-line option `--workflow` to export SISTR results from specific versions of the IRIDA SISTR workflow.
* Add command-line option `--samples-created-since` to export SISTR results from samples created since a particular date or the passed number of days ago.

# Version  0.4.0

* Fixed performance when exporting SISTR results.  Previously, user-run SISTR analyses where included in the results by default, but these took a significant amount of time to export.  Now, only automated SISTR analyses and analyses shared with a project are included by default in the final results.  To revert back to the previous behaviour, you will have to use the `--include-user-results` command-line option.

# Version 0.3.1

* Fixed bug where a user has access to a shared analyses to a project but not access to the samples, causing a failure for all results.
* Removed printing of JSON reponses on use of `--verbose` flag.

# Version 0.3

* Added ability to set a config file using `--config`.
* Fixed broken loading of configuration file located in `~/.local/share/irida-sistr-results/config.ini`.
* Other small error message fixes.

# Version 0.2

* Display URL of IRIDA instance and updated some text on the screen.

# Version 0.1

* Initial release of `irida-sistr-results.py` with the ability to export SISTR results stored in IRIDA to a table (either excel or tab-delimited).
