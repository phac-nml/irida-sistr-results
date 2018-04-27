#!/usr/bin/env python

import argparse
import sys
import os
import shutil
import logging
import getpass
import configparser
import appdirs

from irida_sistr_results.irida_connector import IridaConnector
from irida_sistr_results.irida_api import IridaAPI
from irida_sistr_results.irida_sistr_results import IridaSistrResults
from irida_sistr_results.sistr_writer import SistrCsvWriter, SistrExcelWriter, SistrCsvWriterShort
from irida_sistr_results.version import __version__

script_dir=os.path.dirname(os.path.realpath(__file__))
appname=os.path.basename(__file__)

example_conf_name="config.ini.example"
example_conf_file=script_dir+"/conf/"+example_conf_name

user_conf_dir=appdirs.user_data_dir(os.path.splitext(appname)[0])
user_conf_file=user_conf_dir+'/config.ini'

logger=logging.getLogger("irida-sistr-results")

def main(irida_url,client_id,client_secret,username,password,verbose,projects,tabular_file,excel_file,include_user_results,exclude_user_existing_results,all_projects,timeout,config):
	"""Main method connecting to IRIDA/writing SISTR results file."""
	logging.info("Running "+appname+" version "+__version__)

	connector = IridaConnector(client_id,client_secret,username,password,irida_url,timeout)
	irida_api = IridaAPI(connector)
	irida_results = IridaSistrResults(irida_api,include_user_results,not exclude_user_existing_results)
	
	if all_projects:
		logger.info("Getting results for all projects in IRIDA. This may take a while.")
		sistr_list = irida_results.get_sistr_results_all_projects()
	else:
		logger.info("Getting results for projects: " + str(projects)+". This may take a while.")
		sistr_list = irida_results.get_sistr_results_from_projects(projects)

	total_sample_results=0
	missing_sample_results=0
	pass_sample_results=0
	warn_sample_results=0
	fail_sample_results=0
	total_projects=0
	for proj in sistr_list.keys():
		total_projects+=1
		for result in sistr_list[proj].values():
			total_sample_results+=1
			if (not result.has_sistr_results()):
				missing_sample_results+=1
			elif (result.get_qc_status() == 'PASS'):
				pass_sample_results+=1
			elif (result.get_qc_status() == 'WARNING'):
				warn_sample_results+=1
			elif (result.get_qc_status() == 'FAIL'):
				fail_sample_results+=1
			else:
				logger.error("Somehow got wrong qc info '" + result.get_qc_status()+"'")

	proj_string = 'projects' if (total_projects > 1) else 'project'
	logger.info("Done getting SISTR results\n")
	logger.info("Examined "+str(total_sample_results)+" samples in "+str(total_projects) + ' ' + proj_string + " with status")
	logger.info("PASS:    "+str(pass_sample_results))
	logger.info("WARN:    "+str(warn_sample_results))
	logger.info("FAIL:    "+str(fail_sample_results))
	logger.info("MISSING: "+str(missing_sample_results))

	if tabular_file is not None:
		writer=SistrCsvWriter(irida_url, appname, username, tabular_file)
		writer.write(sistr_list)
		writer.close()
		logger.info("Wrote results to file " + tabular_file)

	if excel_file is not None:
		writer=SistrExcelWriter(irida_url, appname, username, excel_file)
		writer.write(sistr_list)
		writer.close()
		logger.info("Wrote results to file " + excel_file)

def setup_user_data_dir():
	if (not os.path.isdir(user_conf_dir)):
		logger.debug("Directory "+user_conf_dir+" does not exist, creating.")
		os.makedirs(user_conf_dir)

	if (not os.path.exists(user_conf_file)):
		logger.debug("File "+user_conf_file+" does not exist, copying default.")
		shutil.copy(example_conf_file,user_conf_file)
	else:
		logger.debug("File "+user_conf_file+" exists, will not copy default.")

def get_conf_files():
	"""Gets a list of configuration file paths to attempt to read configuration values from."""
	setup_user_data_dir()
	return [script_dir+'/conf/config.ini',
		user_conf_file
		]

def get_conf_files_plus(config_file):
	"""Gets a list of configuration file paths plus the passed config file.

	Args:
	    config_file:  The additional configuration file to include in this list.

	Returns:  The default configuration files plus the user-defined configuration file.
	"""
	l=get_conf_files()
	l.append(config_file)
	return l

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Compile SISTR results from an IRIDA instance into a table.',
		formatter_class=argparse.RawTextHelpFormatter,
		epilog= "\nExample:"+
			"\n\t" + appname + " -a -u irida-user -o out.xlsx"+
			"\n\t\tExports all SISTR results from all projects to a file 'out.xlsx'"+
			"\n\n\t" + appname + " -p 1 -p 2 -u irida-user -o out.xlsx"+
			"\n\t\tExports SISTR results form projects [1,2] to a file 'out.xlsx'")

	parser.add_argument('--irida-url', action='store', dest='irida_url', help='The URL to the IRIDA instance.')
	parser.add_argument('--client-id', action='store', dest='client_id', help='The client id for an IRIDA instance.')
	parser.add_argument('--client-secret', action='store', dest='client_secret', help='The client secret for the IRIDA instance.')
	parser.add_argument('-u', '--username', action='store', dest='username', help='The username for the IRIDA instance.')
	parser.add_argument('--password', action='store', dest='password', help='The password for the IRIDA instance. Prompts for password if left blank.')
	parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Turn on verbose logging.')
	parser.add_argument('-p', '--project', action='append', dest='projects', help='Projects to scan for SISTR results. If left blank will scan all projects the user has access to.')
	parser.add_argument('-a', '--all-projects', action='store_true', dest='all_projects', help='Explicitly load results from all projects the user has access to.  Will ignore the values given in --project.')
	parser.add_argument('--output-tab', '--to-tab-file', action='store', dest='tabular_file', help='Print results to tab-deliminited file.')
	parser.add_argument('-o', '--output-excel', '--to-excel-file', action='store', dest='excel_file', help='Print results to the given excel file.')
	parser.add_argument('--include-user-results', action='store_true', dest='include_user_results', help='Include SISTR analysis results run directly by the user.')
	parser.add_argument('--exclude-user-existing-results', action='store_true', dest='exclude_user_existing_results', help='If including user results, do not replace existing SISTR analysis that were automatically generated with user-run SISTR results.')
	parser.add_argument('-T', '--connection-timeout', action='store', dest='timeout', help='Connection timeout when getting results from IRIDA.')
	parser.add_argument('-c', '--config', action='store', dest='config', help='Configuration file for IRIDA (overrides values in '+str(get_conf_files())+')')
	parser.add_argument('-V', '--version', action='version', version='%(prog)s {}'.format(__version__))

	if len(sys.argv)==1:
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()
	arg_dict = vars(args)

	if (arg_dict['verbose']):
		logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(module)s.%(funcName)s,%(lineno)s: %(message)s')
	else:
		logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


	config=configparser.ConfigParser()

	if (arg_dict['config'] is None):
		config.read(get_conf_files())
	else:
		config.read(get_conf_files_plus(arg_dict['config']))

	if ('irida' in config):
		conf_i = config['irida']
	else:
		logger.warning("No 'irida' information loaded in configuration files.")
		conf_i={}

	try:
		if (arg_dict['irida_url'] is None):
			if 'url' in conf_i:
				arg_dict['irida_url'] = conf_i['url']
			else:
				raise Exception("Must set --irida-url or irida.url in config file ("+str(get_conf_files())+')')
		if (arg_dict['client_id'] is None):
			if 'client_id' in conf_i:
				arg_dict['client_id'] = conf_i['client_id']
			else:
				raise Exception("Must set --client-id or irida.client_id in config file ("+str(get_conf_files())+')')
	
		if (arg_dict['client_secret'] is None):
			if 'client_secret' in conf_i:
				arg_dict['client_secret'] = conf_i['client_secret']
			else:
				raise Exception("Must set --client-secret or irida.client_secret in config file ("+str(get_conf_files())+')')
	
		if (arg_dict['username'] is None):
			if 'username' in conf_i:
				arg_dict['username'] = conf_i['username']
			else:
				raise Exception("Must set --username or irida.username in config file ("+str(get_conf_files())+')')

		if (arg_dict['timeout'] is None):
			if ('timeout' in conf_i and conf_i['timeout'] is not None):
				arg_dict['timeout'] = int(conf_i['timeout'])
			else:
				arg_dict['timeout'] = 600
		elif (type(arg_dict['timeout']) is not int):
			arg_dict['timeout']=int(arg_dict['timeout'])
	
		if (arg_dict['excel_file'] is None and arg_dict['tabular_file'] is None):
			raise Exception("Must use one of --to-tab-file or --to-excel-file [excel-file]")

		if (arg_dict['projects'] is None and arg_dict['all_projects'] is None):
			raise Exception("No --project or --all-projects parameter found.")

		if arg_dict['password'] is None:
			arg_dict['password']=getpass.getpass('Enter password for user="'+arg_dict['username']+'" on IRIDA="'+arg_dict['irida_url']+'": ')
	except Exception as e:
		logging.error(e)
		sys.exit(1)
	
	main(**arg_dict)
