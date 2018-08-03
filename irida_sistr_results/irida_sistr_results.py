import logging

from irida_sistr_results.irida_sistr_workflow import IridaSistrWorkflow

logger = logging.getLogger("irida-sistr-results")


class IridaSistrResults(object):
    """Class for constructing the top-level data structures mapping projects to lists of SISTR results."""

    def __init__(self, irida_api, include_user_results, update_existing_with_user_results,
                 sistr_workflow_versions_or_ids=None, sample_created_min_date=None):
        """
        Creates a new IridaSistrResults object.

        :param irida_api:  The IridaAPI object for connecting to IRIDA.
        :param include_user_results:  Whether or not to include all user-accessible results (or just automated SISTR results).
        :param update_existing_with_user_results:  Whether or not to update existing results with newer results run by a user.
        :param sistr_workflow_versions_or_ids: A list of SISTR workflow versions (or UUIDs) of results to include.
        :param sample_created_min_date: The minimum (oldest) sample created date for samples to include results for.

        :return:  A new IridaSistrResults object.
        """
        self.irida_api = irida_api
        self.include_user_results = include_user_results
        self.update_existing_with_user_results = update_existing_with_user_results
        self.sistr_workflow_ids = IridaSistrWorkflow.workflow_ids_or_versions_to_ids(sistr_workflow_versions_or_ids)
        self.sistr_results = {}
        self.sample_project = {}
        self.sample_created_min_date = sample_created_min_date

    def get_sistr_results_all_projects(self):
        """
        Gets SISTR results from all projects accessible by the current user.

        :return:  All SISTR results from all projects.
        """
        projects = self.irida_api.get_user_projects()
        return self._get_sistr_results(projects)

    def get_sistr_results_from_projects(self, project_ids):
        """
        Gets SISTR results from the list of IRIDA project identifiers.

        :param project_ids:  The list of project ids.

        :return:  All SISTR results from the passed projects.
        """
        projects = []
        for p in project_ids:
            project = self.irida_api.get_user_project(p)
            projects.append(project)

        return self._get_sistr_results(projects)

    def _get_sistr_results(self, projects):
        for p in projects:
            logger.debug("Working on project [" + p['identifier'] + ', ' + p['name'] + ']')
            self._load_sistr_results_for_project(p)
            self._load_sistr_results_shared_to_project(p['identifier'])

        if (self.include_user_results):
            self._load_sistr_results_from_user()

        return self.sistr_results

    def _load_sistr_results_from_user(self):
        user_results = self.irida_api.get_sistr_submissions_for_user(self.sistr_workflow_ids)
        self._load_additional_sistr_results(user_results)

    def _load_sistr_results_shared_to_project(self, project_id):
        project_results = self.irida_api.get_sistr_submissions_shared_to_project(project_id, self.sistr_workflow_ids)
        self._load_additional_sistr_results(project_results)

    def _load_additional_sistr_results(self, additional_results):
        for result in additional_results:
            sample_id = result.get_sample_id()

            if (sample_id in self.sample_project and result.has_sistr_results()):
                for project in self.sample_project[sample_id]:
                    sistr_results_project = self.sistr_results[project]
                    if sample_id in sistr_results_project:
                        if (not sistr_results_project[sample_id].has_sistr_results()):
                            sistr_results_project[sample_id] = result
                        elif (sistr_results_project[
                                  sample_id].get_submission_created_date() < result.get_submission_created_date()):
                            if (self.update_existing_with_user_results):
                                logger.debug(self._result_to_sample_log_string(sistr_results_project[sample_id], result,
                                                                               "older") + " Updating.")
                                sistr_results_project[sample_id] = result
                            else:
                                logger.debug(
                                    "Found result for sample=" + result.get_sample_name() + ". Will not replace with exisiting result.")
                        else:
                            logger.debug(self._result_to_sample_log_string(sistr_results_project[sample_id], result,
                                                                           "newer") + " Not updating.")

    def _load_sistr_results_for_project(self, project):
        project_id = project['identifier']

        if (project_id in self.sistr_results):
            raise Exception("Error: project " + str(project_id) + " already examined")

        self.sistr_results[project_id] = {}
        project_results = self.irida_api.get_sistr_results_for_project(project_id, self.sistr_workflow_ids,
                                                                       self.sample_created_min_date)

        for result in project_results:
            if result is None:
                logger.warning("None result found in project " + str(project_id) + ", will skip")
            else:
                sample_id = result.get_sample_id()
                self.sistr_results[project_id][sample_id] = result
                if (sample_id in self.sample_project):
                    self.sample_project[sample_id].append(project_id)
                else:
                    self.sample_project[sample_id] = [project_id]

    def _timef(self, timestamp):
        return timestamp.isoformat(sep=' ')

    def _result_to_sample_log_string(self, r1, r2, word):
        return "Sample [name=" + r1.get_sample_name() + ", id=" + str(
            r1.get_sample_id()) + "] has exisiting analysis [id=" + r1.get_submission_identifier() + ", created_date=" + self._timef(
            r1.get_submission_created_date()) + "] " + word + " than analysis [id=" + r2.get_submission_identifier() + ", created_date=" + self._timef(
            r2.get_submission_created_date()) + "]."
